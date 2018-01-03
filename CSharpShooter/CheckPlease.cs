// CheckPlease.cs
// Sandox evasion checks forming part of the SharpShooter project
// This is mostly taken from the CheckPlease project
// https://github.com/Arvanaghi/CheckPlease/
//

using System;
using System.Collections.Generic;
using System.IO;
using System.Net.NetworkInformation;
using System.Text.RegularExpressions;

class CheckPlease
{
    // Return value of true means the domain matches the target domain
    public bool isDomain(string domain)
    {
        if (string.Equals(domain, System.Net.NetworkInformation.IPGlobalProperties.GetIPGlobalProperties().DomainName, StringComparison.CurrentCultureIgnoreCase))
        {
            return true;
        }

        return false;
    }

    // Return value of false means we're not on a domain member
    public bool isDomainJoined()
    {
        if (string.Equals("", System.Net.NetworkInformation.IPGlobalProperties.GetIPGlobalProperties().DomainName, StringComparison.CurrentCultureIgnoreCase))
        {
            return false;
        }

        return true;
    }

    // Returns true if possible sandbox artifacts exist on file system
    public bool containsSandboxArtifacts()
    {
        List<string> EvidenceOfSandbox = new List<string>();
        string[] FilePaths = {@"C:\windows\Sysnative\Drivers\Vmmouse.sys",
        @"C:\windows\Sysnative\Drivers\vm3dgl.dll", @"C:\windows\Sysnative\Drivers\vmdum.dll",
        @"C:\windows\Sysnative\Drivers\vm3dver.dll", @"C:\windows\Sysnative\Drivers\vmtray.dll",
        @"C:\windows\Sysnative\Drivers\vmci.sys", @"C:\windows\Sysnative\Drivers\vmusbmouse.sys",
        @"C:\windows\Sysnative\Drivers\vmx_svga.sys", @"C:\windows\Sysnative\Drivers\vmxnet.sys",
        @"C:\windows\Sysnative\Drivers\VMToolsHook.dll", @"C:\windows\Sysnative\Drivers\vmhgfs.dll",
        @"C:\windows\Sysnative\Drivers\vmmousever.dll", @"C:\windows\Sysnative\Drivers\vmGuestLib.dll",
        @"C:\windows\Sysnative\Drivers\VmGuestLibJava.dll", @"C:\windows\Sysnative\Drivers\vmscsi.sys",
        @"C:\windows\Sysnative\Drivers\VBoxMouse.sys", @"C:\windows\Sysnative\Drivers\VBoxGuest.sys",
        @"C:\windows\Sysnative\Drivers\VBoxSF.sys", @"C:\windows\Sysnative\Drivers\VBoxVideo.sys",
        @"C:\windows\Sysnative\vboxdisp.dll", @"C:\windows\Sysnative\vboxhook.dll",
        @"C:\windows\Sysnative\vboxmrxnp.dll", @"C:\windows\Sysnative\vboxogl.dll",
        @"C:\windows\Sysnative\vboxoglarrayspu.dll", @"C:\windows\Sysnative\vboxoglcrutil.dll",
        @"C:\windows\Sysnative\vboxoglerrorspu.dll", @"C:\windows\Sysnative\vboxoglfeedbackspu.dll",
        @"C:\windows\Sysnative\vboxoglpackspu.dll", @"C:\windows\Sysnative\vboxoglpassthroughspu.dll",
        @"C:\windows\Sysnative\vboxservice.exe", @"C:\windows\Sysnative\vboxtray.exe",
        @"C:\windows\Sysnative\VBoxControl.exe"};
        foreach (string FilePath in FilePaths)
        {
            if (File.Exists(FilePath))
            {
                EvidenceOfSandbox.Add(FilePath);
            }
        }

        if (EvidenceOfSandbox.Count == 0)
        {
            return false;
        }
        else
        {
            return true;
        }
    }

    // Return true is machine matches a bad MAC vendor
    public bool isBadMac()
    {
        List<string> EvidenceOfSandbox = new List<string>();

        string[] badMacAddresses = { @"000C29", @"001C14", @"005056", @"000569", @"080027" };

        NetworkInterface[] NICs = NetworkInterface.GetAllNetworkInterfaces();
        foreach (NetworkInterface NIC in NICs)
        {
            foreach (string badMacAddress in badMacAddresses)
            {
                if (NIC.GetPhysicalAddress().ToString().ToLower().Contains(badMacAddress.ToLower()))
                {
                    EvidenceOfSandbox.Add(Regex.Replace(NIC.GetPhysicalAddress().ToString(), ".{2}", "$0:").TrimEnd(':'));
                }
            }
        }

        if (EvidenceOfSandbox.Count == 0)
        {
            return false;
        }
        else
        {
            return true;
        }

    }

    // Return true if a debugger is attached
    public bool isDebugged()
    {
        if (System.Diagnostics.Debugger.IsAttached)
        {
            return true;
        }
        else
        {
            return false;
        }
    }


}
