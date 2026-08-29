<#
.SYNOPSIS
    Decrypt / re-encrypt Metal Gear Solid 4 (Master Collection Vol. 2) .ecf config files.

.DESCRIPTION
    MGS4's engine configs in MGS4\config\ are plain INI text obfuscated with a
    rolling-index XOR. This script converts them to editable text and back, so you
    can change engine settings in Notepad.

    -Apply makes the three changes documented in the README.

    Tested on Windows PowerShell 5.1 and PowerShell 7.6.5.

.EXAMPLE
    .\mgs4ecf.ps1 -Decrypt "D:\Games\...\MGS4\config\mgs4.ecf"
    # edit mgs4.txt in Notepad, then:
    .\mgs4ecf.ps1 -Encrypt "D:\Games\...\MGS4\config\mgs4.txt"

.EXAMPLE
    .\mgs4ecf.ps1 -Apply -GameDir "D:\Games\METAL GEAR SOLID 4 Guns of the Patriots Master Collection Version"
#>
[CmdletBinding(DefaultParameterSetName = 'Show')]
param(
    [Parameter(ParameterSetName = 'Decrypt', Mandatory)][string]$Decrypt,
    [Parameter(ParameterSetName = 'Encrypt', Mandatory)][string]$Encrypt,
    [Parameter(ParameterSetName = 'Apply',   Mandatory)][switch]$Apply,
    [Parameter(ParameterSetName = 'Restore', Mandatory)][switch]$Restore,
    [Parameter(ParameterSetName = 'Interactive', Mandatory)][switch]$Interactive,
    [Parameter(ParameterSetName = 'Show')][switch]$Show,

    [string]$Out,
    [string]$GameDir,
    # Internal render target. Leave at 3840x2160 unless you know why you're changing it -
    # this is a render resolution, not a display resolution. See the README.
    [int]$BufferWidth  = 3840,
    [int]$BufferHeight = 2160,
    [ValidateSet(1, 2, 4, 8, 16)][int]$Aniso = 16,
    [ValidateSet(512, 1024, 2048, 4096)][int]$ShadowBuffer = 4096,
    [switch]$KeepFxaa
)

$ErrorActionPreference = 'Stop'

$script:Key = [System.Text.Encoding]::ASCII.GetBytes('MGS4ConfigFileSecureKey@2024')

# Latin-1 maps bytes 0x00-0xFF onto U+0000-U+00FF one-to-one, so bytes -> text -> bytes
# is lossless. Decoding as UTF-8 would turn any invalid byte into U+FFFD and re-encode
# it as three bytes, silently corrupting the file.
$script:Latin1 = [System.Text.Encoding]::GetEncoding(28591)

function Invoke-EcfXor {
    param([byte[]]$Data)
    $len = $script:Key.Length
    $out = [byte[]]::new($Data.Length)
    for ($i = 0; $i -lt $Data.Length; $i++) {
        $k = ([int][Math]::Floor($i / $len) + $i) % $len
        $out[$i] = $Data[$i] -bxor $script:Key[$k]
    }
    return $out
}

function Read-Ecf {
    param([string]$Path)
    return $script:Latin1.GetString((Invoke-EcfXor ([System.IO.File]::ReadAllBytes($Path))))
}

function Write-Ecf {
    param([string]$Path, [string]$Text)
    [System.IO.File]::WriteAllBytes($Path, (Invoke-EcfXor ($script:Latin1.GetBytes($Text))))
}

function Backup-Once {
    param([string]$Path)
    $bak = "$Path.bak"
    if ((Test-Path -LiteralPath $Path) -and -not (Test-Path -LiteralPath $bak)) {
        Copy-Item -LiteralPath $Path -Destination $bak
        Write-Host "  backed up -> $(Split-Path $bak -Leaf)" -ForegroundColor DarkGray
    }
}

function Resolve-ConfigDir {
    param([string]$Hint)
    $roots = @()
    if ($Hint) { $roots += $Hint }
    $roots += @($PWD.Path, $PSScriptRoot, (Split-Path $PSScriptRoot -Parent))
    foreach ($r in $roots) {
        if (-not $r -or -not (Test-Path -LiteralPath $r)) { continue }
        foreach ($c in @((Join-Path $r 'config'), (Join-Path $r 'MGS4\config'))) {
            if (Test-Path -LiteralPath (Join-Path $c 'mgs4.ecf')) { return (Resolve-Path $c).Path }
        }
    }
    return $null
}

function Show-Settings {
    param([string]$Cfg, [string]$SaveRoot)
    $t = Read-Ecf (Join-Path $Cfg 'mgs4.ecf')
    Write-Host "`nmgs4.ecf" -ForegroundColor Cyan
    foreach ($k in 'dynamicResolution', 'bufferSizeX', 'bufferSizeY', 'windowSizeX', 'windowSizeY', 'vsync', 'fxaa', 'api') {
        $m = [regex]::Match($t, "(?m)^\s*$k\s*=\s*(\S+)")
        if ($m.Success) { Write-Host ('  {0,-20} {1}' -f $k, $m.Groups[1].Value) }
    }
    $scal = Join-Path $Cfg 'mgs4.scalability_PC.ecf'
    if (Test-Path -LiteralPath $scal) {
        $s = Read-Ecf $scal
        $an = [regex]::Matches($s, 'MaxAniso=(\d+)') | ForEach-Object { $_.Groups[1].Value }
        $sh = [regex]::Matches($s, 'ShadowBufferSize=(\d+)') | ForEach-Object { $_.Groups[1].Value }
        Write-Host "`nmgs4.scalability_PC.ecf" -ForegroundColor Cyan
        Write-Host ('  {0,-20} {1}' -f 'MaxAniso (all tiers)', (($an | Select-Object -Unique) -join ' '))
        Write-Host ('  {0,-20} {1}' -f 'ShadowBufferSize', ($sh -join ' '))
    }
    foreach ($sf in @(Get-ChildItem -LiteralPath $SaveRoot -Filter 'mgs4.savedsettings' -Recurse -ErrorAction SilentlyContinue)) {
        Write-Host "`n$($sf.FullName)" -ForegroundColor Cyan
        Get-Content -LiteralPath $sf.FullName | ForEach-Object { Write-Host "  $_" }
    }
    Write-Host ''
}

function Invoke-Restore {
    param([string]$Cfg, [string]$SaveRoot)
    $n = 0
    foreach ($f in @((Join-Path $Cfg 'mgs4.ecf'), (Join-Path $Cfg 'mgs4.scalability_PC.ecf'))) {
        if (Test-Path -LiteralPath "$f.bak") {
            Copy-Item -LiteralPath "$f.bak" -Destination $f -Force
            Write-Host "  restored $(Split-Path $f -Leaf)" -ForegroundColor Green
            $n++
        }
    }
    foreach ($b in @(Get-ChildItem -LiteralPath $SaveRoot -Filter 'mgs4.savedsettings.bak' -Recurse -ErrorAction SilentlyContinue)) {
        Copy-Item -LiteralPath $b.FullName -Destination ($b.FullName -replace '\.bak$', '') -Force
        Write-Host "  restored mgs4.savedsettings" -ForegroundColor Green
        $n++
    }
    if ($n -eq 0) { Write-Host "  nothing to restore - no .bak files found." -ForegroundColor Yellow }
    else { Write-Host "`nRestored $n file(s) to stock." -ForegroundColor Green }
}

function Invoke-Apply {
    param([string]$Cfg, [string]$SaveRoot, [int]$W, [int]$H, [int]$An, [int]$Sh, [bool]$Keep)
    Write-Host "`nApplying..." -ForegroundColor Cyan
    $main = Join-Path $Cfg 'mgs4.ecf'
    Backup-Once $main
    $t = Read-Ecf $main
    $t = [regex]::Replace($t, '(?m)^(\s*dynamicResolution\s*=\s*)\w+', '${1}false')
    $t = [regex]::Replace($t, '(?m)^(\s*bufferSizeX\s*=\s*)\d+', "`${1}$W")
    $t = [regex]::Replace($t, '(?m)^(\s*bufferSizeY\s*=\s*)\d+', "`${1}$H")
    if (-not $Keep) { $t = [regex]::Replace($t, '(?m)^(\s*fxaa\s*=\s*)true', '${1}false') }
    Write-Ecf $main $t
    $fx = if ($Keep) { '' } else { ', fxaa=false' }
    Write-Host "  mgs4.ecf: dynamicResolution=false, buffer=${W}x${H}$fx" -ForegroundColor Green

    $scal = Join-Path $Cfg 'mgs4.scalability_PC.ecf'
    if (Test-Path -LiteralPath $scal) {
        Backup-Once $scal
        $s = Read-Ecf $scal
        # Only touch the "Highest" tier (@3). Tiers 0-2 are the low-spec / Steam Deck ladder;
        # raising their aniso costs performance on exactly the machines that can't spare it.
        $s = [regex]::Replace($s, '(?s)\[TextureGroup@3\][^\[]*', {
            param($m) [regex]::Replace($m.Value, 'MaxAniso=(?!1\b)\d+', "MaxAniso=$An") })
        $s = [regex]::Replace($s, '(?m)^(\s*ShadowBufferSize\s*=\s*)2048', "`${1}$Sh")
        Write-Ecf $scal $s
        Write-Host "  mgs4.scalability_PC.ecf: MaxAniso=$An (Highest tier), ShadowBufferSize=$Sh" -ForegroundColor Green
    }

    if (-not $Keep) {
        foreach ($sf in @(Get-ChildItem -LiteralPath $SaveRoot -Filter 'mgs4.savedsettings' -Recurse -ErrorAction SilentlyContinue)) {
            Backup-Once $sf.FullName
            $c = [System.IO.File]::ReadAllText($sf.FullName)
            $c = [regex]::Replace($c, '(?m)^(enableFXAA=)\w+', '${1}false')
            [System.IO.File]::WriteAllText($sf.FullName, $c)
            Write-Host "  mgs4.savedsettings: enableFXAA=false" -ForegroundColor Green
        }
    }
    Write-Host "`nDone. Run with -Restore to undo.`n" -ForegroundColor Green
}

# ------------------------------------------------------------------ decrypt / encrypt
if ($PSCmdlet.ParameterSetName -eq 'Decrypt') {
    if (-not (Test-Path -LiteralPath $Decrypt)) { throw "No such file: $Decrypt" }
    if (-not $Out) { $Out = [System.IO.Path]::ChangeExtension($Decrypt, '.txt') }
    [System.IO.File]::WriteAllBytes($Out, (Invoke-EcfXor ([System.IO.File]::ReadAllBytes($Decrypt))))
    Write-Host "decrypted -> $Out" -ForegroundColor Green
    return
}

if ($PSCmdlet.ParameterSetName -eq 'Encrypt') {
    if (-not (Test-Path -LiteralPath $Encrypt)) { throw "No such file: $Encrypt" }
    if (-not $Out) { $Out = [System.IO.Path]::ChangeExtension($Encrypt, '.ecf') }
    Backup-Once $Out
    [System.IO.File]::WriteAllBytes($Out, (Invoke-EcfXor ([System.IO.File]::ReadAllBytes($Encrypt))))
    Write-Host "encrypted -> $Out" -ForegroundColor Green
    return
}

# ------------------------------------------------------------------ game-wide modes
$cfg = Resolve-ConfigDir $GameDir
if (-not $cfg) {
    Write-Host "Couldn't find MGS4\config\mgs4.ecf." -ForegroundColor Red
    Write-Host "Run this from your MGS4 install folder, or pass -GameDir '<path>'."
    if ($Interactive) { Write-Host ''; Read-Host 'Press Enter to close' | Out-Null }
    exit 1
}
$gameRoot = Split-Path (Split-Path $cfg -Parent) -Parent
$saveRoot = Join-Path $gameRoot 'mgs4_savedata_win'
Write-Host "config: $cfg" -ForegroundColor DarkGray

switch ($PSCmdlet.ParameterSetName) {
    'Show'    { Show-Settings $cfg $saveRoot }
    'Restore' { Invoke-Restore $cfg $saveRoot }
    'Apply'   { Invoke-Apply $cfg $saveRoot $BufferWidth $BufferHeight $Aniso $ShadowBuffer $KeepFxaa.IsPresent }
    'Interactive' {
        Show-Settings $cfg $saveRoot
        Write-Host '  [1] Apply clarity settings (dynamic res off, FXAA off, 16x AF)'
        Write-Host '  [2] Apply, but keep FXAA on'
        Write-Host '  [3] Restore stock settings'
        Write-Host '  [0] Exit'
        Write-Host ''
        switch ((Read-Host 'Choose')) {
            '1' { Invoke-Apply $cfg $saveRoot $BufferWidth $BufferHeight $Aniso $ShadowBuffer $false }
            '2' { Invoke-Apply $cfg $saveRoot $BufferWidth $BufferHeight $Aniso $ShadowBuffer $true }
            '3' { Invoke-Restore $cfg $saveRoot }
            '0' { Write-Host 'Nothing changed.' }
            default { Write-Host 'Not an option. Nothing changed.' -ForegroundColor Yellow }
        }
        Write-Host ''
        Read-Host 'Press Enter to close' | Out-Null
    }
}
