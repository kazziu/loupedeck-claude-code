namespace Loupedeck.ClaudeMascotPlugin
{
    using System;
    using System.Runtime.InteropServices;

    using Loupedeck.Devices.Loupedeck2Devices;

    // Narzedzie kola CT rysujace caly ekran 240x240 (jak zegar z DefaultWin). Usluga rejestruje je
    // po nazwie klasy, w profilu: wheelPages[].templateName = "WheelToolClawd".
    //   obrot         -> scroll terminala; za szybko = zawroty glowy
    //   dotyk         -> karmienie / budzenie / glaskanie
    //   podwojny      -> taniec
    //   przytrzymanie -> Enter (dawna funkcja kola)
    public class WheelToolClawd : WheelTool
    {
        private const Int32 MOUSEEVENTF_WHEEL = 0x0800;
        private const Byte VK_RETURN = 0x0D;
        private const Int32 KEYEVENTF_KEYUP = 0x0002;

        [DllImport("user32.dll")]
        private static extern void mouse_event(Int32 flags, Int32 dx, Int32 dy, Int32 data, IntPtr extra);

        [DllImport("user32.dll")]
        private static extern void keybd_event(Byte vk, Byte scan, Int32 flags, IntPtr extra);

        public WheelToolClawd()
            : base("Clawd", "Claude Code")
        {
        }

        protected override void OnStart()
        {
            if (ClaudeMascotPlugin.Mascot != null)
            {
                ClaudeMascotPlugin.Mascot.Changed += this.OnChanged;
            }
            this.OnChanged();
        }

        protected override void OnStop()
        {
            if (ClaudeMascotPlugin.Mascot != null)
            {
                ClaudeMascotPlugin.Mascot.Changed -= this.OnChanged;
            }
        }

        private void OnChanged()
        {
            var image = ClaudeMascotPlugin.Mascot?.Render();
            if (image != null && this.IsStarted && !this.IsPaused)
            {
                this.Draw(image);
            }
        }

        protected override BitmapImage CreateImage() => ClaudeMascotPlugin.Mascot?.Render();

        protected override void OnEncoderEvent(DeviceEncoderEvent encoderEvent)
        {
            if (OperatingSystem.IsWindows())
            {
                mouse_event(MOUSEEVENTF_WHEEL, 0, 0, -encoderEvent.Clicks * 120, IntPtr.Zero);
            }
            ClaudeMascotPlugin.Mascot?.Spin(encoderEvent.Clicks);
        }

        protected override void OnTouchEvent(DeviceTouchEvent touchEvent)
        {
            switch (touchEvent.EventType)
            {
                case DeviceTouchEventType.Tap:
                    ClaudeMascotPlugin.Mascot?.Touch();
                    break;
                case DeviceTouchEventType.DoubleTap:
                    ClaudeMascotPlugin.Mascot?.Party();
                    break;
                case DeviceTouchEventType.LongPress:
                    if (OperatingSystem.IsWindows())
                    {
                        keybd_event(VK_RETURN, 0, 0, IntPtr.Zero);
                        keybd_event(VK_RETURN, 0, KEYEVENTF_KEYUP, IntPtr.Zero);
                    }
                    break;
            }
        }
    }
}
