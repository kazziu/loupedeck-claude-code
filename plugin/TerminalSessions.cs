namespace Loupedeck.ClaudeMascotPlugin
{
    using System;
    using System.Collections.Generic;
    using System.Linq;
    using System.Runtime.InteropServices;
    using System.Text;

    // Switches between Claude Code sessions, whether they live in separate Windows Terminal windows or in
    // tabs of one window. With 2+ terminal windows, session N = the N-th window in reading order on screen
    // (top row first, left to right), like a wall of trading terminals; minimized windows go last.
    // With a single window, session N = tab N (Ctrl+Alt+N, a Windows Terminal default).
    internal static class TerminalSessions
    {
        private const String TerminalClass = "CASCADIA_HOSTING_WINDOW_CLASS";
        private const Int32 RowTolerance = 150;   // windows whose tops differ by less than this share a row
        private static Int32 _tab = 1;

        public static void Focus(Int32 n)
        {
            if (!OperatingSystem.IsWindows())
            {
                return;
            }
            var windows = Refresh();
            if (windows.Count >= 2)
            {
                if (n <= windows.Count)
                {
                    Activate(windows[n - 1]);
                }
                return;
            }
            SendTab(n);
        }

        // Dial: +1 / -1 steps through windows (or tabs when there is only one window).
        public static void Step(Int32 diff)
        {
            if (!OperatingSystem.IsWindows() || diff == 0)
            {
                return;
            }
            var windows = Refresh();
            if (windows.Count >= 2)
            {
                var current = windows.IndexOf(GetForegroundWindow());
                var next = ((current < 0 ? 0 : current) + Math.Sign(diff) + windows.Count) % windows.Count;
                Activate(windows[next]);
                return;
            }
            _tab = Math.Clamp(_tab + Math.Sign(diff), 1, 8);
            SendTab(_tab);
        }

        public static void SendTab(Int32 n)
        {
            if (!OperatingSystem.IsWindows() || n < 1 || n > 9)
            {
                return;
            }
            _tab = n;
            var digit = (Byte)('0' + n);
            keybd_event(VK_CONTROL, 0, 0, IntPtr.Zero);
            keybd_event(VK_MENU, 0, 0, IntPtr.Zero);
            keybd_event(digit, 0, 0, IntPtr.Zero);
            keybd_event(digit, 0, KEYEVENTF_KEYUP, IntPtr.Zero);
            keybd_event(VK_MENU, 0, KEYEVENTF_KEYUP, IntPtr.Zero);
            keybd_event(VK_CONTROL, 0, KEYEVENTF_KEYUP, IntPtr.Zero);
        }

        // Visible terminal windows in reading order. Rows are built greedily: a window joins the current row
        // when its top edge is within RowTolerance of the row's first window.
        private static List<IntPtr> Refresh()
        {
            var found = new List<(IntPtr H, RECT R, Boolean Min)>();
            EnumWindows((h, _) =>
            {
                if (IsWindowVisible(h) && ClassOf(h) == TerminalClass && GetWindowRect(h, out var r))
                {
                    found.Add((h, r, IsIconic(h)));
                }
                return true;
            }, IntPtr.Zero);

            var ordered = new List<IntPtr>();
            var onScreen = found.Where(w => !w.Min).OrderBy(w => w.R.Top).ToList();
            while (onScreen.Count > 0)
            {
                var top = onScreen[0].R.Top;
                var row = onScreen.Where(w => w.R.Top - top < RowTolerance).OrderBy(w => w.R.Left).ToList();
                ordered.AddRange(row.Select(w => w.H));
                onScreen.RemoveAll(w => row.Contains(w));
            }
            ordered.AddRange(found.Where(w => w.Min).OrderBy(w => w.H.ToInt64()).Select(w => w.H));
            return ordered;
        }

        // A background process may not steal focus, so attach to the foreground thread first.
        private static void Activate(IntPtr hwnd)
        {
            if (IsIconic(hwnd))
            {
                ShowWindow(hwnd, SW_RESTORE);
            }
            var fg = GetForegroundWindow();
            var fgThread = GetWindowThreadProcessId(fg, out _);
            var me = GetCurrentThreadId();
            var attached = fgThread != me && AttachThreadInput(me, fgThread, true);
            try
            {
                BringWindowToTop(hwnd);
                if (!SetForegroundWindow(hwnd))
                {
                    keybd_event(VK_MENU, 0, 0, IntPtr.Zero);              // the Alt-tap trick unlocks SetForegroundWindow
                    keybd_event(VK_MENU, 0, KEYEVENTF_KEYUP, IntPtr.Zero);
                    SetForegroundWindow(hwnd);
                }
            }
            finally
            {
                if (attached)
                {
                    AttachThreadInput(me, fgThread, false);
                }
            }
        }

        private static String ClassOf(IntPtr h)
        {
            var sb = new StringBuilder(64);
            GetClassName(h, sb, sb.Capacity);
            return sb.ToString();
        }

        private const Byte VK_CONTROL = 0x11, VK_MENU = 0x12;
        private const Int32 KEYEVENTF_KEYUP = 0x0002, SW_RESTORE = 9;

        [StructLayout(LayoutKind.Sequential)]
        private struct RECT
        {
            public Int32 Left, Top, Right, Bottom;
        }

        private delegate Boolean EnumWindowsProc(IntPtr hwnd, IntPtr lParam);

        [DllImport("user32.dll")] private static extern Boolean GetWindowRect(IntPtr h, out RECT r);

        [DllImport("user32.dll")] private static extern Boolean EnumWindows(EnumWindowsProc cb, IntPtr lParam);
        [DllImport("user32.dll", CharSet = CharSet.Unicode)] private static extern Int32 GetClassName(IntPtr h, StringBuilder s, Int32 n);
        [DllImport("user32.dll")] private static extern Boolean IsWindowVisible(IntPtr h);
        [DllImport("user32.dll")] private static extern Boolean IsIconic(IntPtr h);
        [DllImport("user32.dll")] private static extern Boolean ShowWindow(IntPtr h, Int32 cmd);
        [DllImport("user32.dll")] private static extern IntPtr GetForegroundWindow();
        [DllImport("user32.dll")] private static extern Boolean SetForegroundWindow(IntPtr h);
        [DllImport("user32.dll")] private static extern Boolean BringWindowToTop(IntPtr h);
        [DllImport("user32.dll")] private static extern UInt32 GetWindowThreadProcessId(IntPtr h, out UInt32 pid);
        [DllImport("kernel32.dll")] private static extern UInt32 GetCurrentThreadId();
        [DllImport("user32.dll")] private static extern Boolean AttachThreadInput(UInt32 a, UInt32 b, Boolean attach);
        [DllImport("user32.dll")] private static extern void keybd_event(Byte vk, Byte scan, Int32 flags, IntPtr extra);
    }

    // Round buttons 1-8. One class per button keeps the profile action ids simple:
    // "$ClaudeMascot___Loupedeck.ClaudeMascotPlugin.Session3".
    public abstract class SessionButton : PluginDynamicCommand
    {
        private readonly Int32 _n;

        protected SessionButton(Int32 n)
            : base($"Claude session {n}", $"Focus Claude Code session {n} (terminal window, or tab when there is one window)", "Claude sessions", DeviceType.All)
            => this._n = n;

        protected override void RunCommand(String actionParameter) => TerminalSessions.Focus(this._n);
    }

    public class Session1 : SessionButton { public Session1() : base(1) { } }
    public class Session2 : SessionButton { public Session2() : base(2) { } }
    public class Session3 : SessionButton { public Session3() : base(3) { } }
    public class Session4 : SessionButton { public Session4() : base(4) { } }
    public class Session5 : SessionButton { public Session5() : base(5) { } }
    public class Session6 : SessionButton { public Session6() : base(6) { } }
    public class Session7 : SessionButton { public Session7() : base(7) { } }
    public class Session8 : SessionButton { public Session8() : base(8) { } }

    // Dial: previous / next session.
    public class SessionDial : PluginDynamicAdjustment
    {
        public SessionDial()
            : base("Claude sessions", "Step through Claude Code sessions (windows or tabs)", "Claude sessions", false, DeviceType.All)
        {
        }

        protected override void ApplyAdjustment(String actionParameter, Int32 diff) => TerminalSessions.Step(diff);

        protected override String GetAdjustmentValue(String actionParameter) => null;
    }
}
