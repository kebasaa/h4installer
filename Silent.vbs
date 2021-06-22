cmd="py """ + Wscript.Arguments(0) + """ " + WScript.Arguments(1) + " " + WScript.Arguments(2) + " " + WScript.Arguments(3)
CreateObject("WScript.Shell").Run cmd, 0, True
rem MsgBox cmd