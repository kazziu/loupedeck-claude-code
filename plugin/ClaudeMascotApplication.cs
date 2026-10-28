namespace Loupedeck.ClaudeMascotPlugin
{
    using System;

    // The Logi Plugin Service loader requires a ClientApplication class, even in universal plugins.
    public class ClaudeMascotApplication : ClientApplication
    {
        protected override String GetProcessName() => "";

        protected override String GetBundleName() => "";

        public override ClientApplicationStatus GetApplicationStatus() => ClientApplicationStatus.Unknown;
    }
}
