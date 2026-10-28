namespace Loupedeck.ClaudeMascotPlugin
{
    using System;

    // Loader Logi Plugin Service wymaga klasy ClientApplication takze w uniwersalnych wtyczkach.
    public class ClaudeMascotApplication : ClientApplication
    {
        protected override String GetProcessName() => "";

        protected override String GetBundleName() => "";

        public override ClientApplicationStatus GetApplicationStatus() => ClientApplicationStatus.Unknown;
    }
}
