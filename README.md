# MGS4 config tools

Metal Gear Solid 4 in *Master Collection Vol. 2* keeps its engine settings in
`MGS4\config\*.ecf`. Those files are plain INI text run through a simple XOR, so you
can't edit them in Notepad. This repo documents the format, explains which settings
actually affect image quality, and ships a small script — PowerShell on Windows, plain
Python everywhere else — that converts the files to text and back.

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

**`windowSizeX`/`windowSizeY` has to move with it.** Stock keeps these equal to
`bufferSizeX`/`bufferSizeY` (both 3840×2160) — `windowSize` is the actual swapchain the
game presents through, so if you raise or lower the buffer without moving the window to
match, the output stays capped at whatever the window still says and nothing visibly
changes. This tripped up more than one person editing the buffer by hand and getting no
result. `-Apply`/`-BufferWidth`/`-BufferHeight` now move both together automatically.

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

### For weak or low-end hardware

Everything above assumes you have GPU headroom to spend. If you don't — if the game
already sits at a low resolution and still dips into the 20s — do the opposite of
"turn dynamic resolution off": **keep it on** and lower the ceiling it scales from
instead. `dynamicResolution` is the frame-budget scaler described above; on hardware
that's actually missing budget, it's the thing keeping the game playable, not the thing
making it soft.

```
.\mgs4ecf.ps1 -Apply -KeepDynamicRes -BufferWidth 1280 -BufferHeight 720
python3 mgs4ecf.py --apply --keep-dynamic-res --buffer-width 1280 --buffer-height 720
```

This lowers `bufferSize`/`windowSize` to 720p (or lower — there's no floor enforced by
the script; try 960×540 if 720p still isn't enough) while leaving `dynamicResolution =
true`, so the engine can still shrink the viewport further under load instead of being
locked to a single resolution that occasionally can't keep up. **I could not verify**
what floor the scaler itself enforces below a given buffer size — that logic lives in
the binary and I haven't reverse-engineered it — so results below 720p are untested;
try it and see.

### Things I could not verify

- `ShadowSampleCount` — stock is `7` at the highest tier. Raising it is plausible but
  the value may index a fixed kernel table in the binary. Untested; left alone.
- `enablePSOCache` — ships `false`. Turning it on *sounds* like a stutter fix, but
  Konami shipping it off is weak evidence it's incomplete in this build.

---

## A simpler alternative: `mgs4.user.ini`

Credit where it's due: IKobi, in the comments on this mod's Nexus page, found that
dropping a plain-text `mgs4.user.ini` into `MGS4\config\` overrides the encrypted
configs — no decrypt/re-encrypt round trip at all. I checked it against the
binary and it's real: `mgs4.exe` loads `config\mgs4.user.ini` *first*, ahead of
`mgs4.ini`, `mgs4.steam.ini` and `mgs4.input.ini`, and it registers a specific set of
overridable `[render]` keys. The full list I could find in the binary:

```
dynamicResolution, fxaa, fxaaParam, vsync, fullscreen, bufferSizeX, bufferSizeY,
windowSizeX, windowSizeY, backbufferCount, api, enablePSOCache, hardware_occlusion,
fxaa_SteamDeck, fxaa_XBS_X, fxaa_XBS_S, fxaa_PS5, fxaa_Switch_Docked, fxaa_Switch_Handheld
```

So for just the `[render]` settings, this works and needs nothing but a text editor:

```ini
[render]
dynamicResolution = false
fxaa = false
bufferSizeX = 3840
bufferSizeY = 2160
windowSizeX = 3840
windowSizeY = 2160
```

**It does not cover `MaxAniso` or `ShadowBufferSize`.** Those live in
`mgs4.scalability_PC.ecf`'s per-tier `[TextureGroup@n]`/`[Shadow@n]` blocks, and the
only related override I found is `scalability.scalabilityLevel_PC` — which picks a
*tier* (0–3), not an individual value. There's no dotted key for `MaxAniso` or
`ShadowBufferSize` themselves, so raising anisotropy or shadow resolution past what
tier 3 already ships with still needs this repo's `.ecf` editor.

**Still do not** create `config\mgs4.ini`: a stub there appears to shadow the full
`mgs4.ecf` and the game fails to start. `mgs4.user.ini` is the one that's safe.

---

## Using the script

Nothing to install. Unzip into your MGS4 folder — the one containing `MGS4\` and
`mgs4_savedata_win\`.

**Windows:** double-click `Run-MGS4-Clarity-Fix.bat`. The `.bat` is a four-line
wrapper around `mgs4ecf.ps1`. It passes `-ExecutionPolicy Bypass`, which applies to
that one process only — it changes nothing system-wide and needs no admin rights.

**Steam Deck / Linux / macOS:** run `./run-mgs4-clarity-fix.sh` from the game folder
(`chmod +x` it first if the zip didn't preserve the bit). It's a four-line wrapper
around `mgs4ecf.py`, standard library only, Python 3.7+ — no PowerShell needed on
either side.

Either way you get the same menu: apply / apply-but-keep-FXAA / apply-but-keep-dynamic-
resolution / restore.

There is deliberately **no `.exe`** on any platform. Everything here is a few hundred
lines of readable script, and you should be able to see what a tool does before
pointing it at your game files. It also avoids the antivirus false positives that
bundled Python executables reliably attract.

If you'd rather drive it directly:

```powershell
# GitHub marks downloaded files; clear that first or PowerShell refuses to run them
Get-ChildItem . -Recurse | Unblock-File

.\mgs4ecf.ps1 -Show     -GameDir "D:\Games\METAL GEAR SOLID 4 ..."
.\mgs4ecf.ps1 -Apply    -GameDir "D:\Games\METAL GEAR SOLID 4 ..."
.\mgs4ecf.ps1 -Restore  -GameDir "D:\Games\METAL GEAR SOLID 4 ..."
```

```sh
python3 mgs4ecf.py --game-dir "/path/to/MGS4 ..." --apply
python3 mgs4ecf.py --game-dir "/path/to/MGS4 ..." --restore
```

Drop `-GameDir`/`--game-dir` when running from inside the game folder. Tested on
Windows PowerShell 5.1 and PowerShell 7.6.5.

It writes a `.bak` next to each file before the first change and never overwrites an
existing one, so `-Restore`/`--restore` always returns you to stock. If there's nothing
to restore it says so rather than claiming success.

Useful flags: `-KeepFxaa`/`--keep-fxaa` to leave anti-aliasing on,
`-KeepDynamicRes`/`--keep-dynamic-res` to leave the frame-budget scaler on (see
[weak hardware](#for-weak-or-low-end-hardware) above), `-Aniso`/`--aniso`,
`-ShadowBuffer`/`--shadow-buffer`, and `-BufferWidth`/`-BufferHeight`
(`--buffer-width`/`--buffer-height`) to move the render target — up for more
supersampling, down for more headroom. `windowSize` now always follows the buffer
automatically, since stock keeps the two equal and the game presents through the window.

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
Vol. 2 PC release. Framerate work is cipherxof's. The `mgs4.user.ini` override is
IKobi's find, from the comments on this mod's Nexus page.

MIT licensed.
