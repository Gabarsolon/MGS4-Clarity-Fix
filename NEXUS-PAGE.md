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
prints your current settings, then offers apply / apply-but-keep-FXAA / restore.

A [i].bak[/i] is written before the first change and never overwritten, so restore
always returns you to stock. Steam Deck users: [i]python3 mgs4ecf.py --interactive[/i]

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

[size=4][b]What this will not fix[/b][/size]

MGS4 is a 2008 PS3 game that rendered at 1024x768 internally, and the Master
Collection is a port of that build rather than a remake. Some softness lives in the
source assets and no config edit touches it. This sharpens what can be sharpened.

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

## Upload settings

- **Requirements:** none
- **Permissions:** MIT, so allow redistribution and modification
- **Do not upload** `mgs4ecf.exe` — Nexus virus-scans uploads, and an opaque
  bundled-Python binary invites both false positives and user suspicion
- Credit cipherxof for MGSFPSUnlock by link only; do not bundle it
