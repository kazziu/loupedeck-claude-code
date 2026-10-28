namespace Loupedeck.ClaudeMascotPlugin
{
    using System;
    using System.Runtime.InteropServices;

    // Dotyk ekranu kola: karmienie (gdy glodny), budzenie albo glaskanie.
    public class TamagotchiCommand : PluginDynamicCommand
    {
        public TamagotchiCommand()
            : base("Clawd", "Tamagotchi Claude Code: dotknij, zeby poglaskac albo nakarmic", "Clawd", DeviceType.All)
        {
        }

        protected override Boolean OnLoad()
        {
            if (ClaudeMascotPlugin.Mascot != null)
            {
                ClaudeMascotPlugin.Mascot.Changed += this.OnChanged;
            }
            return true;
        }

        protected override Boolean OnUnload()
        {
            if (ClaudeMascotPlugin.Mascot != null)
            {
                ClaudeMascotPlugin.Mascot.Changed -= this.OnChanged;
            }
            return true;
        }

        private void OnChanged() => this.ActionImageChanged();

        protected override void RunCommand(String actionParameter) => ClaudeMascotPlugin.Mascot?.Touch();

        protected override BitmapImage GetCommandImage(String actionParameter, PluginImageSize imageSize) =>
            ClaudeMascotPlugin.Mascot?.Render();

        protected override String GetCommandDisplayName(String actionParameter, PluginImageSize imageSize) => "Clawd";
    }

    // Obrot kola: scroll w terminalu (jak zwykle) + maskotka krecaca sie za szybko dostaje zawrotow glowy.
    public class TamagotchiScroll : PluginDynamicAdjustment
    {
        private const Int32 MOUSEEVENTF_WHEEL = 0x0800;

        [DllImport("user32.dll")]
        private static extern void mouse_event(Int32 flags, Int32 dx, Int32 dy, Int32 data, IntPtr extra);

        public TamagotchiScroll()
            : base("Clawd scroll", "Scroll historii terminala; za szybko = Clawd ma zawroty glowy", "Clawd", false, DeviceType.All)
        {
        }

        protected override Boolean OnLoad()
        {
            if (ClaudeMascotPlugin.Mascot != null)
            {
                ClaudeMascotPlugin.Mascot.Changed += this.OnChanged;
            }
            return true;
        }

        protected override Boolean OnUnload()
        {
            if (ClaudeMascotPlugin.Mascot != null)
            {
                ClaudeMascotPlugin.Mascot.Changed -= this.OnChanged;
            }
            return true;
        }

        private void OnChanged() => this.ActionImageChanged();

        protected override void ApplyAdjustment(String actionParameter, Int32 diff)
        {
            if (OperatingSystem.IsWindows())
            {
                mouse_event(MOUSEEVENTF_WHEEL, 0, 0, -diff * 120, IntPtr.Zero);
            }
            ClaudeMascotPlugin.Mascot?.Spin(diff);
        }

        protected override BitmapImage GetAdjustmentImage(String actionParameter, PluginImageSize imageSize) =>
            ClaudeMascotPlugin.Mascot?.Render();

        protected override String GetAdjustmentValue(String actionParameter) => null;
    }
}
