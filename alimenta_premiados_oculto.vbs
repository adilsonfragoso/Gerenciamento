Set WshShell = CreateObject("WScript.Shell")
WshShell.Run "python """ & WScript.ScriptFullName & """ ..\\alimenta_premiados.py --oculto", 0
Set WshShell = Nothing 