namespace Loupedeck.ClaudeMascotPlugin
{
    using System;

    // Uniwersalna wtyczka (bez aplikacji docelowej): maskotka-tamagotchi na kole Loupedeck CT.
    public class ClaudeMascotPlugin : Plugin
    {
        public override Boolean UsesApplicationApiOnly => true;

        public override Boolean HasNoApplication => true;

        internal static Mascot Mascot { get; private set; }

        public override void Load()
        {
            // klatki sa wbudowane w DLL (host laduje wtyczke z pamieci, Assembly.Location jest puste)
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
