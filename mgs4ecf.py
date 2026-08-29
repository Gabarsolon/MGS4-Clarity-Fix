#!/usr/bin/env python3
"""Decrypt / re-encrypt MGS4 (Master Collection Vol. 2) .ecf config files.

The .ecf files are INI text XORed with a rolling-index key. See the README for the
format; this is just a convenience wrapper. Standard library only, Python 3.7+.
"""

import argparse
import re
import shutil
import sys
from pathlib import Path

KEY = b'MGS4ConfigFileSecureKey@2024'


def xor(data: bytes) -> bytes:
    """Symmetric cipher used by the .ecf files. Same function both directions."""
    n = len(KEY)
    return bytes(b ^ KEY[((i // n) + i) % n] for i, b in enumerate(data))


# Latin-1 round-trips every byte 0x00-0xFF exactly. UTF-8 would turn invalid bytes
# into U+FFFD and re-encode them as three bytes, silently corrupting the file.
def read_ecf(path: Path) -> str:
    return xor(path.read_bytes()).decode('latin-1')


def write_ecf(path: Path, text: str) -> None:
    path.write_bytes(xor(text.encode('latin-1')))


def backup_once(path: Path) -> None:
    bak = path.with_name(path.name + '.bak')
    if path.exists() and not bak.exists():
        shutil.copyfile(path, bak)
        print(f'  backed up -> {bak.name}')


def app_dir() -> Path:
    """Directory the user actually launched us from.

    Under PyInstaller, __file__ points inside the temporary _MEIxxxx extraction
    directory, not next to the .exe -- so a frozen build that trusts __file__ can
    never find a game sitting beside it. sys.executable is the real location.
    """
    if getattr(sys, 'frozen', False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent


def find_config(hint=None):
    roots = [Path(hint)] if hint else []
    roots += [Path.cwd(), app_dir(), app_dir().parent]
    for r in roots:
        for c in (r / 'config', r / 'MGS4' / 'config'):
            if (c / 'mgs4.ecf').exists():
                return c.resolve()
    return None


def cmd_show(cfg: Path) -> None:
    text = read_ecf(cfg / 'mgs4.ecf')
    print('\nmgs4.ecf')
    for k in ('dynamicResolution', 'bufferSizeX', 'bufferSizeY', 'windowSizeX',
              'windowSizeY', 'vsync', 'fxaa', 'api'):
        m = re.search(rf'^\s*{k}\s*=\s*(\S+)', text, re.M)
        if m:
            print(f'  {k:<20} {m.group(1)}')
    scal = cfg / 'mgs4.scalability_PC.ecf'
    if scal.exists():
        s = read_ecf(scal)
        print('\nmgs4.scalability_PC.ecf')
        print(f"  {'MaxAniso (all tiers)':<20} "
              f"{' '.join(dict.fromkeys(re.findall(r'MaxAniso=(\d+)', s)))}")
        print(f"  {'ShadowBufferSize':<20} "
              f"{' '.join(re.findall(r'ShadowBufferSize=(\d+)', s))}")
    print()


def cmd_apply(cfg: Path, saves: Path, width: int, height: int, aniso: int,
              shadow: int, keep_fxaa: bool) -> None:
    print('\nApplying...')
    main = cfg / 'mgs4.ecf'
    backup_once(main)
    t = read_ecf(main)
    t = re.sub(r'(?m)^(\s*dynamicResolution\s*=\s*)\w+', r'\1false', t)
    t = re.sub(r'(?m)^(\s*bufferSizeX\s*=\s*)\d+', rf'\g<1>{width}', t)
    t = re.sub(r'(?m)^(\s*bufferSizeY\s*=\s*)\d+', rf'\g<1>{height}', t)
    if not keep_fxaa:
        t = re.sub(r'(?m)^(\s*fxaa\s*=\s*)true', r'\1false', t)
    write_ecf(main, t)
    print(f'  mgs4.ecf: dynamicResolution=false, buffer={width}x{height}'
          f'{"" if keep_fxaa else ", fxaa=false"}')

    scal = cfg / 'mgs4.scalability_PC.ecf'
    if scal.exists():
        backup_once(scal)
        s = read_ecf(scal)
        # Only the "Highest" tier. @0-@2 are the low-spec / Steam Deck ladder, and
        # MaxAniso=1 on TG_UI / TG_NoMip is deliberate.
        s = re.sub(r'(?s)\[TextureGroup@3\][^\[]*',
                   lambda m: re.sub(r'MaxAniso=(?!1\b)\d+', f'MaxAniso={aniso}', m.group(0)), s)
        s = re.sub(r'(?m)^(\s*ShadowBufferSize\s*=\s*)2048', rf'\g<1>{shadow}', s)
        write_ecf(scal, s)
        print(f'  mgs4.scalability_PC.ecf: MaxAniso={aniso} (Highest tier), '
              f'ShadowBufferSize={shadow}')

    if not keep_fxaa and saves.exists():
        for sf in saves.glob('*/mgs4/mgs4.savedsettings'):
            backup_once(sf)
            sf.write_text(re.sub(r'(?m)^(enableFXAA=)\w+', r'\1false',
                                 sf.read_text(encoding='utf-8', errors='surrogateescape')),
                          encoding='utf-8', errors='surrogateescape')
            print('  mgs4.savedsettings: enableFXAA=false')

    print('\nDone. Run with --restore to undo.\n')


def cmd_restore(cfg: Path, saves: Path) -> None:
    n = 0
    for name in ('mgs4.ecf', 'mgs4.scalability_PC.ecf'):
        p, bak = cfg / name, cfg / (name + '.bak')
        if bak.exists():
            shutil.copyfile(bak, p)
            print(f'  restored {name}')
            n += 1
    if saves.exists():
        for bak in saves.glob('*/mgs4/mgs4.savedsettings.bak'):
            shutil.copyfile(bak, bak.with_suffix(''))
            print('  restored mgs4.savedsettings')
            n += 1
    print(f'\nRestored {n} file(s) to stock.\n' if n
          else '  nothing to restore - no .bak files found.\n')


def cmd_interactive(cfg: Path, saves: Path, width: int, height: int, aniso: int,
                    shadow: int) -> None:
    cmd_show(cfg)
    print('  [1] Apply clarity settings (dynamic res off, FXAA off, 16x AF)')
    print('  [2] Apply, but keep FXAA on')
    print('  [3] Restore stock settings')
    print('  [0] Exit\n')
    choice = input('Choose: ').strip()
    if choice == '1':
        cmd_apply(cfg, saves, width, height, aniso, shadow, False)
    elif choice == '2':
        cmd_apply(cfg, saves, width, height, aniso, shadow, True)
    elif choice == '3':
        cmd_restore(cfg, saves)
    elif choice == '0':
        print('Nothing changed.')
    else:
        print('Not an option. Nothing changed.')


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument('--game-dir')
    ap.add_argument('--apply', action='store_true')
    ap.add_argument('--interactive', action='store_true')
    ap.add_argument('--restore', action='store_true')
    ap.add_argument('--decrypt', metavar='FILE')
    ap.add_argument('--encrypt', metavar='FILE')
    ap.add_argument('--out', metavar='FILE')
    # bufferSize is a render target, not a display resolution. Read the README before
    # lowering it -- 3840x2160 supersamples down to your monitor and is the sharp path.
    ap.add_argument('--buffer-width', type=int, default=3840)
    ap.add_argument('--buffer-height', type=int, default=2160)
    ap.add_argument('--aniso', type=int, default=16, choices=[1, 2, 4, 8, 16])
    ap.add_argument('--shadow-buffer', type=int, default=4096,
                    choices=[512, 1024, 2048, 4096])
    ap.add_argument('--keep-fxaa', action='store_true')
    args = ap.parse_args()

    for flag, ext in (('decrypt', '.txt'), ('encrypt', '.ecf')):
        src = getattr(args, flag)
        if src:
            src = Path(src)
            if not src.exists():
                print(f'No such file: {src}', file=sys.stderr)
                return 1
            out = Path(args.out) if args.out else src.with_suffix(ext)
            out.write_bytes(xor(src.read_bytes()))
            print(f'{flag}ed -> {out}')
            return 0

    # A frozen build launched by double-click gets no arguments, and a bare settings
    # dump in a window that closes instantly is useless. Default it to the menu.
    interactive = args.interactive or (
        getattr(sys, 'frozen', False)
        and not (args.apply or args.restore or args.game_dir))

    cfg = find_config(args.game_dir)
    if not cfg:
        print("Couldn't find MGS4/config/mgs4.ecf.\n"
              "Put this next to the game, run it from the MGS4 install folder, "
              "or pass --game-dir <path>.", file=sys.stderr)
        if interactive:
            input('\nPress Enter to close: ')
        return 1
    print(f'config: {cfg}')
    saves = cfg.parent.parent / 'mgs4_savedata_win'

    if args.restore:
        cmd_restore(cfg, saves)
    elif args.apply:
        cmd_apply(cfg, saves, args.buffer_width, args.buffer_height,
                  args.aniso, args.shadow_buffer, args.keep_fxaa)
    elif interactive:
        cmd_interactive(cfg, saves, args.buffer_width, args.buffer_height,
                        args.aniso, args.shadow_buffer)
    else:
        cmd_show(cfg)

    if interactive:
        input('\nPress Enter to close: ')
    return 0


if __name__ == '__main__':
    sys.exit(main())
