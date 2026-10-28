namespace Loupedeck.ClaudeMascotPlugin
{
    using System;

    using Loupedeck.Devices.Loupedeck2Devices;

    // CT wheel tool that draws the whole 240x240 screen (like the DefaultWin clock). Reference it in the
    // profile as wheelPages[].templateName = "ClaudeMascot___WheelToolClawd" (plugin prefix required).
    //   rotate     -> scroll the terminal; too fast = dizzy
    //   tap        -> feed / wake up / pet
    //   double tap -> dance
    //   long press -> Enter (the wheel's old job)
    public class WheelToolClawd : WheelTool
    {
        public WheelToolClawd()
            : base("Clawd", "Claude Code")
        {
        }

        protected override void OnStart()
        {
            if (ClaudeMascotPlugin.Mascot != null)
            {
                ClaudeMascotPlugin.Mascot.Changed += this.OnChanged;
                ClaudeMascotPlugin.Mascot.Buzz += this.OnBuzz;
            }
            this.OnChanged();
        }

        protected override void OnStop()
        {
            if (ClaudeMascotPlugin.Mascot != null)
            {
                ClaudeMascotPlugin.Mascot.Changed -= this.OnChanged;
                ClaudeMascotPlugin.Mascot.Buzz -= this.OnBuzz;
            }
        }

        // Claude is waiting for a decision: short wheel vibration (the service corrects an unknown waveform index).
        private void OnBuzz()
        {
            try
            {
                this.Vibrate(1);
            }
            catch (Exception)
            {
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
            NativeInput.Scroll(encoderEvent.Clicks);
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
                    NativeInput.Enter();
                    break;
            }
        }
    }
}
