[Setup]
AppName=AirBattery
AppVersion=1.0
DefaultDirName={autopf}\AirBattery
DefaultGroupName=AirBattery
OutputDir=C:\Users\sgarg\Documents\airpods\Publicar
OutputBaseFilename=Instalar_AirBattery
SetupIconFile=C:\Users\sgarg\Documents\airpods\AirBattery_Release\installer.ico
UninstallDisplayIcon={app}\AirBatteryMonitor.exe
Compression=lzma
SolidCompression=yes
ArchitecturesInstallIn64BitMode=x64
PrivilegesRequired=admin
ShowLanguageDialog=yes
CloseApplications=yes

[Languages]
Name: "spanish"; MessagesFile: "compiler:Languages\Spanish.isl"
Name: "english"; MessagesFile: "compiler:Default.isl"
Name: "portuguese"; MessagesFile: "compiler:Languages\Portuguese.isl"

[CustomMessages]
spanish.StartupTask=Ejecutar AirBattery automáticamente al iniciar Windows
english.StartupTask=Run AirBattery automatically when Windows starts
portuguese.StartupTask=Executar AirBattery automaticamente ao iniciar o Windows

spanish.StartupGroup=Opciones de inicio:
english.StartupGroup=Startup options:
portuguese.StartupGroup=Opções de inicialização:

spanish.LaunchDesc=Lanzar AirBattery ahora
english.LaunchDesc=Launch AirBattery now
portuguese.LaunchDesc=Iniciar AirBattery agora

[Tasks]
Name: "startup"; Description: "{cm:StartupTask}"; GroupDescription: "{cm:StartupGroup}";
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "C:\Users\sgarg\Documents\airpods\AirBattery_Release\AirBatteryMonitor.exe"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\AirBattery"; Filename: "{app}\AirBatteryMonitor.exe"
Name: "{autodesktop}\AirBattery"; Filename: "{app}\AirBatteryMonitor.exe"; Tasks: desktopicon

[Registry]
Root: HKCU; Subkey: "Software\Microsoft\Windows\CurrentVersion\Run"; ValueType: string; ValueName: "AirpodsBatteryMonitor"; ValueData: """{app}\AirBatteryMonitor.exe"""; Tasks: startup; Flags: uninsdeletevalue

[Run]
Filename: "{app}\AirBatteryMonitor.exe"; Description: "{cm:LaunchDesc}"; Flags: nowait postinstall skipifsilent

[UninstallRun]
Filename: "{cmd}"; Parameters: "/C taskkill /F /IM AirBatteryMonitor.exe /T"; Flags: runhidden waituntilterminated
Filename: "{cmd}"; Parameters: "/C taskkill /F /IM AirBattery.exe /T"; Flags: runhidden waituntilterminated
