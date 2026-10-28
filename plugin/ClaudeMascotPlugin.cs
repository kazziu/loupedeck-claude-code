namespace Loupedeck.ClaudeMascotPlugin
{
    using System;

    // Universal plugin (no target application): the tamagotchi mascot on the Loupedeck CT wheel.
    public class ClaudeMascotPlugin : Plugin
    {
        public override Boolean UsesApplicationApiOnly => true;

        public override Boolean HasNoApplication => true;

        internal static Mascot Mascot { get; private set; }

        public override void Load()
        {
            // frames are embedded in the DLL (the host loads plugins from memory, so Assembly.Location is empty)
            Mascot = new Mascot(typeof(ClaudeMascotPlugin).Assembly);
            Mascot.Start();
        }

        public override void Unload()
        {
            Mascot?.Dispose();
            Mascot = null;
        }
    }
}
