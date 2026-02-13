# Inno Setup ile Setup.exe üretmek için
# Ön koşul: Inno Setup kurulu olmalı (ISCC.exe PATH'te olmalı)

$ErrorActionPreference = 'Stop'

# 1) Önce exe'yi üret
powershell -ExecutionPolicy Bypass -File .\build_exe.ps1

# 2) Setup.exe üret
# ISCC.exe bulunamazsa kullanıcıdan Inno Setup kurması istenir.
$iss = Join-Path $PSScriptRoot 'installer_inno.iss'

$cmd = Get-Command ISCC.exe -ErrorAction SilentlyContinue

if (-not $cmd) {
    $candidates = @(
        "$env:ProgramFiles\Inno Setup 6\ISCC.exe",
        "$env:ProgramFiles(x86)\Inno Setup 6\ISCC.exe",
        "$env:ProgramFiles\Inno Setup 5\ISCC.exe",
        "$env:ProgramFiles(x86)\Inno Setup 5\ISCC.exe",
        "C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
    )

    $found = $null
    foreach ($p in $candidates) {
        if ($p -and (Test-Path $p)) { $found = $p; break }
    }

    if ($found) {
        & $found $iss
        Write-Host 'Tamam: Setup.exe üretildi. Çıktı klasörü: installer_output' -ForegroundColor Green
        exit 0
    }

    $compilCandidates = @(
        "$env:ProgramFiles\Inno Setup 6\Compil32.exe",
        "$env:ProgramFiles(x86)\Inno Setup 6\Compil32.exe",
        "C:\Program Files (x86)\Inno Setup 6\Compil32.exe"
    )

    $compil = $null
    foreach ($p in $compilCandidates) {
        if ($p -and (Test-Path $p)) { $compil = $p; break }
    }

    if ($compil) {
        $dir = Split-Path -Parent $compil
        $iscc2 = Join-Path $dir 'ISCC.exe'
        if (Test-Path $iscc2) {
            & $iscc2 $iss
        } else {
            # Compil32 supports command-line compile with /cc
            & $compil /cc $iss
        }
        Write-Host 'Tamam: Setup.exe üretildi. Çıktı klasörü: installer_output' -ForegroundColor Green
        exit 0
    }

    Write-Host 'HATA: ISCC.exe bulunamadı (PATH veya standart kurulum dizinlerinde yok).' -ForegroundColor Red
    Write-Host 'Çözüm: Inno Setup kurulumunu kontrol et ve tekrar dene.' -ForegroundColor Red
    Write-Host 'Inno Setup: https://jrsoftware.org/isinfo.php'
    exit 1
}

& $cmd.Source $iss

Write-Host 'Tamam: Setup.exe üretildi. Çıktı klasörü: installer_output' -ForegroundColor Green
