namespace Loupedeck.ClaudeMascotPlugin
{
    using System;
    using System.Runtime.InteropServices;

    // Scroll and Enter for the wheel: user32 on Windows, CGEvent on macOS. Posting CGEvents needs the
    // Accessibility permission, which LogiPluginService already has for its keyboard macros.
    internal static class NativeInput
    {
        private const Int32 MOUSEEVENTF_WHEEL = 0x0800;
        private const Byte VK_RETURN = 0x0D;
        private const Int32 KEYEVENTF_KEYUP = 0x0002;

        private const Int32 LinesPerClick = 3;      // one Windows wheel notch (120) scrolls 3 lines
        private const UInt16 kVK_Return = 36;
        private const UInt32 kCGScrollEventUnitLine = 1;
        private const UInt32 kCGHIDEventTap = 0;
        private const String CoreGraphics = "/System/Library/Frameworks/CoreGraphics.framework/CoreGraphics";
        private const String CoreFoundation = "/System/Library/Frameworks/CoreFoundation.framework/CoreFoundation";

        // clicks > 0 = wheel turned clockwise = scroll down
        public static void Scroll(Int32 clicks)
        {
            if (OperatingSystem.IsWindows())
            {
                mouse_event(MOUSEEVENTF_WHEEL, 0, 0, -clicks * 120, IntPtr.Zero);
            }
            else if (OperatingSystem.IsMacOS())
            {
                // CGEventCreateScrollWheelEvent is variadic (unsafe to P/Invoke on arm64); the "2" variant is not.
                Post(CGEventCreateScrollWheelEvent2(IntPtr.Zero, kCGScrollEventUnitLine, 1, -clicks * LinesPerClick, 0, 0));
            }
        }

        public static void Enter()
        {
            if (OperatingSystem.IsWindows())
            {
                keybd_event(VK_RETURN, 0, 0, IntPtr.Zero);
                keybd_event(VK_RETURN, 0, KEYEVENTF_KEYUP, IntPtr.Zero);
            }
            else if (OperatingSystem.IsMacOS())
            {
                Post(CGEventCreateKeyboardEvent(IntPtr.Zero, kVK_Return, true));
                Post(CGEventCreateKeyboardEvent(IntPtr.Zero, kVK_Return, false));
            }
        }

        private static void Post(IntPtr ev)
        {
            if (ev == IntPtr.Zero)
            {
                return;
            }
            CGEventPost(kCGHIDEventTap, ev);
            CFRelease(ev);
        }

        [DllImport("user32.dll")]
        private static extern void mouse_event(Int32 flags, Int32 dx, Int32 dy, Int32 data, IntPtr extra);

        [DllImport("user32.dll")]
        private static extern void keybd_event(Byte vk, Byte scan, Int32 flags, IntPtr extra);

        [DllImport(CoreGraphics)]
        private static extern IntPtr CGEventCreateScrollWheelEvent2(IntPtr source, UInt32 units, UInt32 wheelCount, Int32 wheel1, Int32 wheel2, Int32 wheel3);

        [DllImport(CoreGraphics)]
        private static extern IntPtr CGEventCreateKeyboardEvent(IntPtr source, UInt16 keyCode, [MarshalAs(UnmanagedType.I1)] Boolean keyDown);

        [DllImport(CoreGraphics)]
        private static extern void CGEventPost(UInt32 tap, IntPtr ev);

        [DllImport(CoreFoundation)]
        private static extern void CFRelease(IntPtr obj);
    }
}
