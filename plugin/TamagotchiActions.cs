namespace Loupedeck.ClaudeMascotPlugin
{
    using System;
    using System.Runtime.InteropServices;

    // Touching the wheel screen: feed (when hungry), wake up or pet. Can also be placed on a tile.
    public class TamagotchiCommand : PluginDynamicCommand
    {
        public TamagotchiCommand()
            : base("Clawd", "Claude Code tamagotchi: tap to pet or feed", "Clawd", DeviceType.All)
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

    // Turning the wheel: scrolls the terminal as usual; spin too fast and the mascot gets dizzy.
    public class TamagotchiScroll : PluginDynamicAdjustment
    {
        private const Int32 MOUSEEVENTF_WHEEL = 0x0800;

        [DllImport("user32.dll")]
        private static extern void mouse_event(Int32 flags, Int32 dx, Int32 dy, Int32 data, IntPtr extra);

        public TamagotchiScroll()
            : base("Clawd scroll", "Scrolls the terminal; too fast and Clawd gets dizzy", "Clawd", false, DeviceType.All)
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
