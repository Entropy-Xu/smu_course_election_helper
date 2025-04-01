; 脚本由 Inno Setup 脚本向导 生成！
; 有关创建 Inno Setup 脚本文件的详细资料请查阅帮助文档！

#define MyAppName "Smu_Course_Election_Helper"
#define MyAppVersion "2.1"
#define MyAppPublisher "Hong"
#define MyAppURL "https://github.com/EricHongXDD/smu_course_election_helper"
#define MyAppExeName "Smu_Course_Election_Helper_2.1.exe"

[Setup]
; 注: AppId的值为单独标识该应用程序。
; 不要为其他安装程序使用相同的AppId值。
; (若要生成新的 GUID，可在菜单中点击 "工具|生成 GUID"。)
AppId={{C2892DC2-B752-4549-A3AD-C7BB18FACAC1}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
;AppVerName={#MyAppName} {#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={autopf}\{#MyAppName}
DisableProgramGroupPage=yes
; 以下两行的路径需要根据您的实际环境修改
; InfoBeforeFile=D:\code\works\smu_course_election_helper-2.0-TKGUI\dist\license.txt
; InfoAfterFile=D:\code\works\smu_course_election_helper-2.0-TKGUI\dist\finish.txt
; 以下行取消注释，以在非管理安装模式下运行（仅为当前用户安装）。
;PrivilegesRequired=lowest
OutputDir=dist
OutputBaseFilename=Smu_Course_Election_Helper_Setup_2.1
Compression=lzma
SolidCompression=yes
WizardStyle=modern

[Languages]
Name: "chinesesimp"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
; 以下路径需要根据您的实际环境修改
Source: "dist\Smu_Course_Election_Helper_2.1\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\Smu_Course_Election_Helper_2.1\_internal\*"; DestDir: "{app}\_internal"; Flags: ignoreversion recursesubdirs createallsubdirs
; 注意: 不要在任何共享系统文件上使用"Flags: ignoreversion"

[Icons]
Name: "{autoprograms}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon
 