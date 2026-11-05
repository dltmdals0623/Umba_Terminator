[Setup]
AppId={{D3465D3A-271B-4358-8A78-5DBC026A0BC6}
AppName=UmbaTerminator
AppVersion=1.0.0
AppPublisherURL=https://github.com/dltmdals0623
WizardStyle=modern
ArchitecturesInstallIn64BitMode=x64compatible
LicenseFile=LICENSE
DefaultDirName={autopf}\UmbaTerminator
DefaultGroupName=UmbaTerminator
OutputDir=output
OutputBaseFilename=UmbaTerminator_Setup
SetupIconFile=images\icon.ico
UninstallDisplayIcon={app}\umbaTerminator.exe
PrivilegesRequired=lowest
Compression=lzma
SolidCompression=yes

[Languages]
Name: "korean"; MessagesFile: "compiler:Languages\Korean.isl"

[Tasks]
Name: "autostart"; Description: "Windows 시작 시 자동 실행"

[Files]
Source: "dist\umbaTerminator.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "README.md"; DestDir: "{app}"; Flags: isreadme
Source: "images\*"; DestDir: "{app}\images"; Flags: recursesubdirs

[Icons]
Name: "{group}\UmbaTerminator"; Filename: "{app}\umbaTerminator.exe"
Name: "{userstartup}\UmbaTerminator"; Filename: "{app}\umbaTerminator.exe"; Tasks: autostart

[Run]
Filename: "{app}\umbaTerminator.exe"; Description: "지금 실행"; Flags: nowait postinstall skipifsilent
