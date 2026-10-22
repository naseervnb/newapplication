[Setup]
AppName=Naseer Image & Video Compressor
AppVersion=1.0
DefaultDirName={pf}\NaseerCompressor
DefaultGroupName=Naseer Image & Video Compressor
OutputDir=F:\test\newApp\dist
OutputBaseFilename=Setup_NaseerCompressor
Compression=lzma
SolidCompression=yes

[Files]
Source: "F:\test\newApp\dist\compress_app.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "F:\test\newApp\dist\ffmpeg\*"; DestDir: "{app}\ffmpeg"; Flags: ignoreversion recursesubdirs

[Icons]
Name: "{group}\Naseer Image & Video Compressor"; Filename: "{app}\compress_app.exe"
Name: "{commondesktop}\Naseer Image & Video Compressor"; Filename: "{app}\compress_app.exe"

[Run]
Filename: "{app}\compress_app.exe"; Description: "Launch Naseer Image & Video Compressor"; Flags: nowait postinstall skipifsilent
