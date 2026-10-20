Option Explicit
Dim shell, folder, launcher
Set shell = CreateObject("WScript.Shell")
folder = CreateObject("Scripting.FileSystemObject").GetParentFolderName(WScript.ScriptFullName)
launcher = Chr(34) & folder & "\INICIAR_MASTERBROKER_DEMO.cmd" & Chr(34)
shell.Run launcher, 0, False

