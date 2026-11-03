[Setup]
AppName=Optiflow
AppVersion=1.6
DefaultDirName={autopf}\Optiflow
DefaultGroupName=Optiflow
UninstallDisplayIcon={app}\Optiflow.exe
OutputDir=Output
OutputBaseFilename=Optiflow_Setup_v1.6
Compression=lzma2
SolidCompression=yes
WizardStyle=modern

[Tasks]
; This defines the "desktopicon" task so the [Icons] section doesn't error out
Name: "desktopicon"; Description: "Create a &desktop icon"; GroupDescription: "Additional icons:"

[Files]
Source: "dist\Optiflow\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{autoprograms}\Optiflow"; Filename: "{app}\Optiflow.exe"; IconFilename: "{app}\Optiflow.exe"
Name: "{autodesktop}\Optiflow"; Filename: "{app}\Optiflow.exe"; IconFilename: "{app}\Optiflow.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\Optiflow.exe"; Description: "Launch Optiflow"; Flags: nowait postinstall skipifsilent