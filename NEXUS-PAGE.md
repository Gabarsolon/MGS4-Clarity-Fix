# Nexus Mods page copy

Not part of the tool — paste-ready text for the Nexus upload form.
Game: **Metal Gear Solid - Master Collection**  ·  Category: **Miscellaneous**

---

## Mod name

```
MGS4 Clarity Fix - Disable Dynamic Resolution Scaling and FXAA
```

## Short description (350 char limit)

```
MGS4 ships with dynamic resolution scaling on. The engine shrinks the 3D viewport under GPU load while the HUD stays native, which is why the world looks soft but the UI looks sharp. This unlocks the encrypted .ecf engine configs and turns that off, along with FXAA. Includes a general .ecf editor. Readable scripts, no .exe, one-click restore.
```

---

## Description (Nexus BBCode)

```bbcode
[size=4][b]What this fixes[/b][/size]

MGS4 ships with [b]dynamic resolution scaling enabled[/b] in its engine config. The
engine watches GPU frame time and shrinks the 3D viewport inside the render target
when it goes over budget — but the HUD still composites at full resolution. That is
exactly why people describe the world looking soft while the UI stays crisp. The
developer debug panel for it is still sitting in the executable.

This turns it off, along with the default FXAA pass, by unlocking the encrypted
[i].ecf[/i] config files the game keeps in [i]MGS4\config\[/i].

[size=4][b]What it changes[/b][/size]

[list]
[*][b]dynamicResolution[/b] true → false (stops the viewport scaler)
[*][b]fxaa[/b] true → false (removes the post-process blur)
[*][b]MaxAniso[/b] 8 → 16, highest quality tier only
[*][b]ShadowBufferSize[/b] 2048 → 4096
[*][b]enableFXAA[/b] false in your savedsettings, so the in-game toggle agrees
[/list]

Only the "Highest" texture tier is touched. The lower tiers are the low-spec and
Steam Deck ladder, and raising anisotropy there costs performance on exactly the
machines that can least afford it.

[size=4][b]Install[/b][/size]

Unzip into your MGS4 folder — the one containing [i]MGS4\[/i] and
[i]mgs4_savedata_win\[/i] — and double-click [b]Run-MGS4-Clarity-Fix.bat[/b]. It
prints your current settings, then offers apply / apply-but-keep-FXAA /
apply-but-keep-dynamic-resolution / restore.

A [i].bak[/i] is written before the first change and never overwritten, so restore
always returns you to stock. Steam Deck / Linux / macOS: run
[i]./run-mgs4-clarity-fix.sh[/i] instead — same script, standard-library Python,
no PowerShell needed.

[b]Low-end GPU and it still dips into the 20s?[/b] Do the opposite of this mod's
default: keep dynamic resolution on and lower the ceiling it scales from —
[i]-Apply -KeepDynamicRes -BufferWidth 1280 -BufferHeight 720[/i] (or
[i]--apply --keep-dynamic-res --buffer-width 1280 --buffer-height 720[/i] on the
Python side). The scaler is what keeps weak hardware playable; this mod's default
turns it off on purpose because it assumes you have headroom to spend.

[size=4][b]There is no .exe in this download[/b][/size]

Everything here is readable script — a four-line .bat, a PowerShell script, and a
Python equivalent. You should be able to see what a tool does before pointing it at
your game files, and bundled-Python executables reliably trip antivirus heuristics.

[size=4][b]Do not lower bufferSize to match your monitor[/b][/size]

If you go editing the config yourself, know that [b]bufferSizeX/Y is the internal
render target, not your display resolution[/b]. Konami ships a per-platform ladder
that tracks GPU power: PC 3840x2160, Xbox Series S 2560x1440, Switch 1920x1080. On PC
the game renders at 4K and downsamples to your monitor, which is supersampling.

Setting it to "match your native resolution" throws that away. It reads like a
sharpening tweak and does the opposite — combined with FXAA off you land at native
resolution with no anti-aliasing at all. This mod leaves it at 3840x2160.

Editing it yourself? [i]windowSizeX/Y[/i] has to move with [i]bufferSizeX/Y[/i] —
stock keeps them equal, and [i]windowSize[/i] is the actual swapchain the game
presents through. Change one without the other and nothing visibly happens. The
script now moves both together automatically.

[size=4][b]What this will not fix[/b][/size]

MGS4 is a 2008 PS3 game that rendered at 1024x768 internally, and the Master
Collection is a port of that build rather than a remake. Some softness lives in the
source assets and no config edit touches it. This sharpens what can be sharpened.

[size=4][b]A plaintext alternative for basic settings[/b][/size]

Credit to IKobi in the comments below: a plain-text [i]mgs4.user.ini[/i] dropped into
[i]MGS4\config\[/i] overrides [i][render][/i] keys directly (confirmed against the
binary — see the GitHub README for the full key list), no decrypt/re-encrypt needed.
It does not cover [i]MaxAniso[/i] or [i]ShadowBufferSize[/i] — those still need this
mod's [i].ecf[/i] editor.

[size=4][b]For modders: the .ecf format[/b][/size]

The [i].ecf[/i] files are INI text XORed with the 28-byte ASCII key
[i]MGS4ConfigFileSecureKey@2024[/i]. The key index advances one position per full
cycle: [i]key[((i // 28) + i) % 28][/i]. Symmetric, no checksum or header. The
included script exposes this as [i]-Decrypt[/i] / [i]-Encrypt[/i] so you can edit any
engine config in Notepad.

[size=4][b]Framerate[/b][/size]

Out of scope here. Use [url=https://github.com/cipherxof/MGSFPSUnlock]MGSFPSUnlock by
cipherxof[/url], which is the mod that actually solves it — the engine's timestep is a
hardcoded 1/60 constant, so config edits alone cannot unlock the framerate without
running the simulation fast.

[size=4][b]Source[/b][/size]

[url=https://github.com/Gabarsolon/MGS4-Clarity-Fix]github.com/Gabarsolon/MGS4-Clarity-Fix[/url] — MIT licensed.
```

---

## Description (plain text fallback)

Nexus's newer editor is rich-text and may render BBCode literally instead of parsing
it. Paste the BBCode version above first; if you see `[b]` tags on screen instead of
bold text, undo and paste this instead, then bold the headings by hand.

```
WHAT THIS FIXES

MGS4 ships with dynamic resolution scaling enabled in its engine config. The engine
watches GPU frame time and shrinks the 3D viewport inside the render target when it
goes over budget - but the HUD still composites at full resolution. That is exactly
why people describe the world looking soft while the UI stays crisp. The developer
debug panel for it is still sitting in the executable.

This turns it off, along with the default FXAA pass, by unlocking the encrypted .ecf
config files the game keeps in MGS4\config\.

WHAT IT CHANGES

- dynamicResolution: true to false (stops the viewport scaler)
- fxaa: true to false (removes the post-process blur)
- MaxAniso: 8 to 16, highest quality tier only
- ShadowBufferSize: 2048 to 4096
- enableFXAA: false in your savedsettings, so the in-game toggle agrees

Only the "Highest" texture tier is touched. The lower tiers are the low-spec and Steam
Deck ladder, and raising anisotropy there costs performance on exactly the machines
that can least afford it.

INSTALL

Unzip into your MGS4 folder - the one containing MGS4\ and mgs4_savedata_win\ - and
double-click Run-MGS4-Clarity-Fix.bat. It prints your current settings, then offers
apply / apply-but-keep-FXAA / apply-but-keep-dynamic-resolution / restore.

A .bak is written before the first change and never overwritten, so restore always
returns you to stock. Steam Deck / Linux / macOS: run ./run-mgs4-clarity-fix.sh
instead - same script, standard-library Python, no PowerShell needed.

Low-end GPU and it still dips into the 20s? Do the opposite of this mod's default:
keep dynamic resolution on and lower the ceiling it scales from -
-Apply -KeepDynamicRes -BufferWidth 1280 -BufferHeight 720 (or
--apply --keep-dynamic-res --buffer-width 1280 --buffer-height 720 on the Python
side). The scaler is what keeps weak hardware playable; this mod's default turns it
off on purpose because it assumes you have headroom to spend.

THERE IS NO .EXE IN THIS DOWNLOAD

Everything here is readable script - a four-line .bat, a PowerShell script, and a
Python equivalent. You should be able to see what a tool does before pointing it at
your game files, and bundled-Python executables reliably trip antivirus heuristics.

DO NOT LOWER BUFFERSIZE TO MATCH YOUR MONITOR

If you go editing the config yourself, know that bufferSizeX/Y is the internal render
target, not your display resolution. Konami ships a per-platform ladder that tracks GPU
power: PC 3840x2160, Xbox Series S 2560x1440, Switch 1920x1080. On PC the game renders
at 4K and downsamples to your monitor, which is supersampling.

Setting it to "match your native resolution" throws that away. It reads like a
sharpening tweak and does the opposite - combined with FXAA off you land at native
resolution with no anti-aliasing at all. This mod leaves it at 3840x2160.

Editing it yourself? windowSizeX/Y has to move with bufferSizeX/Y - stock keeps them
equal, and windowSize is the actual swapchain the game presents through. Change one
without the other and nothing visibly happens. The script now moves both together
automatically.

WHAT THIS WILL NOT FIX

MGS4 is a 2008 PS3 game that rendered at 1024x768 internally, and the Master Collection
is a port of that build rather than a remake. Some softness lives in the source assets
and no config edit touches it. This sharpens what can be sharpened.

A PLAINTEXT ALTERNATIVE FOR BASIC SETTINGS

Credit to IKobi in the comments below: a plain-text mgs4.user.ini dropped into
MGS4\config\ overrides [render] keys directly (confirmed against the binary - see
the GitHub README for the full key list), no decrypt/re-encrypt needed. It does not
cover MaxAniso or ShadowBufferSize - those still need this mod's .ecf editor.

FOR MODDERS: THE .ECF FORMAT

The .ecf files are INI text XORed with the 28-byte ASCII key
MGS4ConfigFileSecureKey@2024. The key index advances one position per full cycle:
key[((i // 28) + i) % 28]. Symmetric, no checksum or header. The included script
exposes this as -Decrypt / -Encrypt so you can edit any engine config in Notepad.

FRAMERATE

Out of scope here. Use MGSFPSUnlock by cipherxof, which is the mod that actually
solves it - the engine's timestep is a hardcoded 1/60 constant, so config edits alone
cannot unlock the framerate without running the simulation fast.
https://github.com/cipherxof/MGSFPSUnlock

SOURCE

https://github.com/Gabarsolon/MGS4-Clarity-Fix - MIT licensed.
```

---

## Tags

Add these three:

- **Quality of Life** — fits: it removes a default that degrades the image
- **Utilities for Players** — fits: the `.ecf` decrypt/encrypt tool is a general utility
- **Bug Fixes** — defensible, since most people experience the scaler as a defect

Skip **Performance Optimization**. It is the honest opposite: pinning the render
target and raising anisotropy costs frames, it just buys image quality with them.

Optional: **Nexus Mods Turns 25** enters the 25th Anniversary Charity Mod Drive —
donation points go to Doctors Without Borders and Nexus matches. Costs nothing.

## Media (required — one image minimum)

A real before/after screenshot pair is worth more than anything else you could put
here, and it is what will make people believe the page.

You have to launch the game to verify the config anyway, so capture it in the same
sitting:

1. `-Restore` to stock, launch, find a scene with strong oblique ground texture and a
   hard shadow edge — the Middle East street in Act 1 works well.
2. Screenshot from a fixed standing position. Do not move.
3. Quit, `-Apply`, relaunch, return to the same spot, screenshot again.
4. Upload as "Before (stock)" and "After (fix applied)".

Same resolution, same time of day, same camera angle. If the difference is hard to
see in stills, say so on the page rather than overselling it — dynamic resolution is
load-dependent, so the gap widens on weaker GPUs and during heavy scenes.

## Upload settings

- **Mod version:** `1.1.0` to match the GitHub tag, rather than `1.1` — bumped from
  `1.0.0` for the `-KeepDynamicRes` flag, the `windowSize` sync fix, and the Linux
  `.sh` launcher, all added in response to issues reported after the first release
- **Requirements:** none
- **Permissions:** MIT, so allow redistribution and modification
- **Files:** upload `MGS4-Clarity-Fix-v1.1.0.zip` as the main file, replacing
  `MGS4-Clarity-Fix-v1.0.0.zip`
- **Do not upload** `mgs4ecf.exe` — Nexus virus-scans uploads, and an opaque
  bundled-Python binary invites both false positives and user suspicion
- Credit cipherxof for MGSFPSUnlock by link only; do not bundle it

## On the AI-Generated Content tag

Nexus's **AI-Generated Content** tag is aimed at generated *assets* — upscaled
textures, synthesised voice lines, AI art. This mod contains none of those: it ships
scripts and a config diff. On a literal reading the tag does not apply, and applying
it would misfile the mod alongside asset packs people filter for different reasons.

That said, this was built with AI assistance, and the modding community currently
treats undisclosed AI involvement as a trust problem rather than a licensing one. The
cheap, honest move is a line at the bottom of the description:

```
Built with AI assistance. The .ecf cipher and the engine behaviour described above
were verified against the game binary and the shipped config files, not guessed.
```

That is accurate — the key, the config keys and the dynamic-resolution debug strings
were all read out of `mgs4.exe` and the `.ecf` files directly.

**Do not** use an AI-generated image to satisfy the Media requirement. That would be
generated content, it would require the tag, and a fabricated "before/after" for a
graphics mod is the one thing that would genuinely burn the page.
