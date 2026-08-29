# MGS4 config tools

Metal Gear Solid 4 in *Master Collection Vol. 2* keeps its engine settings in
`MGS4\config\*.ecf`. Those files are plain INI text run through a simple XOR, so you
can't edit them in Notepad. This repo documents the format, explains which settings
actually affect image quality, and ships a small PowerShell script that converts the
files to text and back.

You do not need the script. The whole thing is one XOR — [everything it does is
documented below](#doing-it-by-hand) so you can do it by hand or write your own.

---

## Why the game looks soft

Three separate things get blamed for this and they aren't equally real. Worth being
precise, because two of them are fixable and one isn't.

**1. Dynamic resolution is on by default.** `mgs4.ecf` ships with
`dynamicResolution = true`. This is a genuine GPU-time-budget scaler — the engine
watches frame time and shrinks the 3D viewport inside the render target when it goes
over budget. The binary still contains the developer debug panel for it, which reads:

```
Viewport percentage: %0i
Buffer    Width: %0i    Height: %0i
Adjusted    Width: %0i    Height: %0i
Weighted average gpu time (ms): %0.1f
Panic(ms): %0.1f    Budget(ms): %0.1f    HeadRoom: %0.1f    Margin: %0.1f
Change threshold: %0.2f    Frame number before change: %0i
```

The UI is composited at full buffer resolution, the 3D scene isn't. That's exactly the
"only the UI looks native" symptom people describe on Steam Deck. Turning this off is
the one change here with a clear mechanism behind it, and it matters most on hardware
that's actually missing the frame budget.

**2. FXAA is on by default.** It's a post-process blur and turning it off does sharpen
edges. But be honest about the ceiling: people report the softness persists with FXAA
off, so this is not the whole story.

**3. The game is from 2008 and rendered at 1024×768 internally on PS3.** The Master
Collection is a port of that build, not a remake. Assets, LODs and effect buffers are
what they are. No config edit fixes this, and anyone promising a "crystal clear" MGS4
is overselling it.

## The one thing not to do

`bufferSizeX` / `bufferSizeY` is the **internal render target**, not your display
resolution. Konami ships a per-platform ladder that tracks GPU power:

| Platform | bufferSize |
|---|---|
| PC | 3840×2160 |
| Xbox Series S | 2560×1440 |
| Switch | 1920×1080 |

PC gets a 4K render target regardless of your monitor. On a 1440p display the stock
config renders at 4K and downsamples — that's supersampling, and it's the sharpest
thing in the config.

Setting `bufferSize` to "match your monitor" **throws that away**. It looks like a
1:1-native-pixel-mapping optimisation and it is the exact opposite. Combined with
FXAA off you end up at native res with no anti-aliasing at all, which aliases and
shimmers worse than stock. Leave it at 3840×2160, or raise it if you have headroom.

---

## What to change

Three edits in `MGS4\config\`:

| File | Setting | Stock | Change to | Why |
|---|---|---|---|---|
| `mgs4.ecf` | `dynamicResolution` | `true` | `false` | stops the viewport scaler |
| `mgs4.ecf` | `fxaa` | `true` | `false` | removes the post-process blur |
| `mgs4.scalability_PC.ecf` | `MaxAniso` in `[TextureGroup@3]` | `8` | `16` | sharper oblique surfaces |

Optional: `ShadowBufferSize` under `[Shadow@3]` from `2048` to `4096`.

Also set `enableFXAA=false` in
`mgs4_savedata_win\<SteamID>\mgs4\mgs4.savedsettings` — that one is already plain
text, and it's the in-game toggle, so it needs to agree with the engine config.

Only touch `[TextureGroup@3]`. Tiers `@0`–`@2` are the low-spec and Steam Deck ladder;
raising anisotropy there costs performance on the machines least able to afford it.
Leave the `MaxAniso=1` entries on `TG_UI` and `TG_NoMip` alone.

### Things I could not verify

- `ShadowSampleCount` — stock is `7` at the highest tier. Raising it is plausible but
  the value may index a fixed kernel table in the binary. Untested; left alone.
- `enablePSOCache` — ships `false`. Turning it on *sounds* like a stutter fix, but
  Konami shipping it off is weak evidence it's incomplete in this build.
- `config\mgs4.user.ini` — the executable contains this path string alongside
  `config\mgs4.ini`, `config\mgs4.steam.ini` and `config\mgs4.input.ini`, which
  suggests a plaintext override mechanism that would make this whole repo unnecessary.
  **Do not** create `config\mgs4.ini`: a stub there appears to shadow the full
  `mgs4.ecf`, and the game fails to start. `mgs4.user.ini` alone is untested.

---

## Using the script

`mgs4ecf.ps1` needs no install. Tested on Windows PowerShell 5.1 and PowerShell 7.6.5.

```powershell
# GitHub marks downloaded files; clear that first or PowerShell refuses to run it
Unblock-File .\mgs4ecf.ps1

# see what you currently have
.\mgs4ecf.ps1 -Show -GameDir "D:\Games\METAL GEAR SOLID 4 ..."

# apply the three changes above
.\mgs4ecf.ps1 -Apply -GameDir "D:\Games\METAL GEAR SOLID 4 ..."

# put everything back
.\mgs4ecf.ps1 -Restore -GameDir "D:\Games\METAL GEAR SOLID 4 ..."
```

Drop the `-GameDir` if you run it from inside the game folder. If your policy blocks
scripts, prefix with `powershell -ExecutionPolicy Bypass -File .\mgs4ecf.ps1`.

It writes a `.bak` next to each file before the first change and never overwrites an
existing one, so `-Restore` always returns you to stock. If there's nothing to restore
it says so rather than claiming success.

Useful flags: `-KeepFxaa` to leave anti-aliasing on, `-Aniso`, `-ShadowBuffer`, and
`-BufferWidth`/`-BufferHeight` if you want to *raise* the render target above 4K.

There's a Python equivalent, `mgs4ecf.py`, for Steam Deck and Linux.

## Doing it by hand

The script is a convenience, not a dependency. The format:

`.ecf` files are INI text XORed byte-by-byte with the 28-byte ASCII key
`MGS4ConfigFileSecureKey@2024`. The key index advances slightly faster than the data
index, so the key walks forward one position every full cycle:

```python
key = b'MGS4ConfigFileSecureKey@2024'
out = bytes(b ^ key[((i // len(key)) + i) % len(key)] for i, b in enumerate(data))
```

It's symmetric — the same function encrypts and decrypts. There's no checksum, length
field or header, so an edited file just needs to be valid INI. Sizes may differ from
stock and that's fine.

One trap if you write your own: decode the bytes as **Latin-1**, not UTF-8. Latin-1
maps `0x00`–`0xFF` one-to-one onto `U+0000`–`U+00FF`, so the round-trip is lossless.
UTF-8 turns any invalid byte into `U+FFFD` and re-encodes it as three bytes, silently
corrupting and lengthening the file.

---

## Framerate

Out of scope here — use [cipherxof/MGSFPSUnlock](https://github.com/cipherxof/MGSFPSUnlock).

Worth knowing why config edits can't do this: `fpsLimiter` in `mgs4.savedsettings` is
clamped on load against `FPS_PC` in `mgs4.scalability_PC.ecf`, and raising both still
lands you at 60 because the engine's timestep is a hardcoded constant. `mgs4.exe`
carries the double `1/60` at `0x1418b63d0` and the float `0.016666668f` written into
the viewport init at `0x1407051f0`, and subsystems read the resulting delta from a
fixed struct offset. Unlocking the framerate without running the simulation fast means
hooking each of those, which is what MGSFPSUnlock does.

## Credits

The blur symptoms and the 1024×768 detail come from
[r/metalgearsolid](https://www.reddit.com/r/metalgearsolid/) threads following the
Vol. 2 PC release. Framerate work is cipherxof's.

MIT licensed.
