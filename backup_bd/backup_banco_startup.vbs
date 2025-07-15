Set objShell = CreateObject("WScript.Shell")
Set objFSO = CreateObject("Scripting.FileSystemObject")

' Obtem o diretorio do script atual
strPath = objFSO.GetParentFolderName(WScript.ScriptFullName)

' Executa o BAT sem mostrar janela
objShell.Run """" & strPath & "\backup_banco_controle.bat""", 0, False
