; Inno Setup script
; Output: Setup.exe
; Prerequisite: Inno Setup (ISCC.exe)

#define MyAppName "Toplu QR Kod Etiket"
#define MyAppExeName "QR_Etiket_PDF.exe"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "İlyas YEŞİL"

[Setup]
AppId={{0B4B5A7B-7F6D-4A15-A2C7-7F7A7B2B2B5A}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes
OutputDir=installer_output
OutputBaseFilename=Setup
Compression=lzma
SolidCompression=yes
WizardStyle=modern
SetupIconFile=QR_icon_01.ico

[Languages]
Name: "turkish"; MessagesFile: "compiler:Languages\Turkish.isl"

[Files]
Source: "dist\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion
Source: "QR_icon_01.ico"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{autoprograms}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; WorkingDir: "{app}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon; WorkingDir: "{app}"

[Tasks]
Name: "desktopicon"; Description: "Masaüstü kısayolu oluştur"; GroupDescription: "Ek görevler:"; Flags: unchecked

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "Uygulamayı çalıştır"; Flags: nowait postinstall skipifsilent
