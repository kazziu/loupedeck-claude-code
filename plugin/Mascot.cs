namespace Loupedeck.ClaudeMascotPlugin
{
    using System;
    using System.Collections.Generic;
    using System.IO;
    using System.Reflection;
    using System.Text.Json;
    using System.Threading;

    // Tamagotchi: stan, statystyki i skladanie klatek (pixel art z art/pixelart.py -> frames/*.png).
    // Dwa zrodla zachowan:
    //   1. wlasne zycie maskotki (spacer, sen, glod, taniec) i dotyk/obrot kola,
    //   2. stan sesji Claude Code z hookow (~/.config/loupedeck-cc/sessions/*.json, patrz hooks/mascot_hook.py).
    // Stan Claude ma pierwszenstwo, ale swiezy dotyk uzytkownika na chwile wygrywa.
    internal sealed class Mascot : IDisposable
    {
        private const Int32 TickMs = 120;
        private const Int32 SessionPollTicks = 8;      // ~1 s
        private static readonly TimeSpan SleepAfter = TimeSpan.FromMinutes(3);
        private static readonly TimeSpan FullHungerAfter = TimeSpan.FromMinutes(45);
        private static readonly TimeSpan UserLock = TimeSpan.FromSeconds(4);

        // priorytet stanow Claude (wyzej = wazniejszy) -> animacja
        private static readonly String[] ClaudePriority = { "idle", "working", "hello", "done", "compact", "oops", "attention" };
        private static readonly Dictionary<String, String> ClaudeAnimation = new()
        {
            ["working"] = "work", ["hello"] = "hello", ["done"] = "done",
            ["compact"] = "squish", ["oops"] = "oops", ["attention"] = "attention",
        };

        private readonly Object _lock = new();
        private readonly Random _rnd = new();
        private readonly Dictionary<String, BitmapImage[]> _frames = new();
        private readonly String _sessionsDir;
        private BitmapImage _floor;
        private Int32 _scale = 6, _center = 20, _minX = 17, _maxX = 23;
        private Timer _timer;

        private String _state = "idle";
        private Int32 _frame, _ticksLeft, _x = 20, _targetX = 20, _poll;
        private Double _hunger = 20, _spin;
        private DateTime _lastTouch = DateTime.Now, _userLockUntil = DateTime.MinValue;
        private String _claude = "idle";
        private Int32 _working, _waiting;

        public event Action Changed;

        // Claude zaczal czekac na uzytkownika (do wibracji kola).
        public event Action Buzz;

        public Mascot(Assembly assembly)
        {
            this._sessionsDir = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.UserProfile),
                ".config", "loupedeck-cc", "sessions");
            Byte[] Res(String name)
            {
                using var s = assembly.GetManifestResourceStream("frames." + name);
                using var ms = new MemoryStream();
                s.CopyTo(ms);
                return ms.ToArray();
            }
            try
            {
                using var doc = JsonDocument.Parse(Res("frames.json"));
                var root = doc.RootElement;
                this._scale = root.GetProperty("scale").GetInt32();
                this._center = this._x = this._targetX = root.GetProperty("center").GetInt32();
                this._minX = root.GetProperty("walk_x")[0].GetInt32();
                this._maxX = root.GetProperty("walk_x")[1].GetInt32();
                foreach (var st in root.GetProperty("states").EnumerateObject())
                {
                    var arr = new BitmapImage[st.Value.GetInt32()];
                    for (var i = 0; i < arr.Length; i++)
                    {
                        arr[i] = BitmapImage.FromArray(Res($"{st.Name}_{i}.png"));
                    }
                    this._frames[st.Name] = arr;
                }
                this._floor = BitmapImage.FromArray(Res("floor.png"));
            }
            catch (Exception)
            {
                // brak klatek: Render() zwroci prosty placeholder
            }
        }

        public void Start() => this._timer = new Timer(_ => this.Tick(), null, TickMs, TickMs);

        public void Dispose() => this._timer?.Dispose();

        // --- interakcje ------------------------------------------------------------------------------
        public void Touch()
        {
            lock (this._lock)
            {
                this.UserActed();
                if (this._state == "sleep")
                {
                    this.Set("happy", 16);                 // obudzony, ale zadowolony
                }
                else if (this._hunger > 40)
                {
                    this._hunger = 0;
                    this.Set("eat", 16 * 2);              // dwie porcje chrupania
                    this._userLockUntil = DateTime.Now.AddSeconds(4);
                }
                else
                {
                    this.Set(this._rnd.Next(2) == 0 ? "pet" : "happy", 16);
                }
            }
            this.Changed?.Invoke();
        }

        public void Party()
        {
            lock (this._lock)
            {
                this.UserActed();
                this.Set("dance", 40);
            }
            this.Changed?.Invoke();
        }

        public void Spin(Int32 diff)
        {
            lock (this._lock)
            {
                this._lastTouch = DateTime.Now;
                this._spin += Math.Abs(diff);
                if (this._spin > 14 && this._state != "dizzy")
                {
                    this.UserActed();
                    this.Set("dizzy", 30);
                }
                else if (this._state == "sleep")
                {
                    this.Set("idle", 10);
                }
            }
        }

        private void UserActed()
        {
            this._lastTouch = DateTime.Now;
            this._userLockUntil = DateTime.Now + UserLock;
        }

        // --- petla -----------------------------------------------------------------------------------
        private void Tick()
        {
            Boolean buzz = false;
            lock (this._lock)
            {
                this._frame++;
                this._spin *= 0.85;
                this._hunger = Math.Min(100, this._hunger + 100.0 * TickMs / FullHungerAfter.TotalMilliseconds);

                if (++this._poll % SessionPollTicks == 0)
                {
                    var before = this._claude;
                    this.ReadSessions();
                    buzz = this._claude == "attention" && before != "attention";
                    if (this._claude != before)
                    {
                        this._ticksLeft = 0;              // reaguj od razu
                    }
                }

                if (this._state.StartsWith("walk") && this._frame % 2 == 0)
                {
                    this._x += Math.Sign(this._targetX - this._x);
                    if (this._x == this._targetX)
                    {
                        this._ticksLeft = 0;
                    }
                }

                if (--this._ticksLeft <= 0)
                {
                    this.ChooseNext();
                }
            }
            if (buzz)
            {
                this.Buzz?.Invoke();
            }
            this.Changed?.Invoke();
        }

        private void ChooseNext()
        {
            if (DateTime.Now < this._userLockUntil)
            {
                this._ticksLeft = 4;                       // dokoncz reakcje na dotyk
                return;
            }
            if (ClaudeAnimation.TryGetValue(this._claude, out var anim))
            {
                this.Set(anim, SessionPollTicks);
                return;
            }

            var bored = DateTime.Now - this._lastTouch;
            if (bored > SleepAfter)
            {
                this.Set("sleep", 60);
            }
            else if (this._hunger > 70 && this._rnd.NextDouble() < 0.5)
            {
                this.Set("hungry", 24);
            }
            else
            {
                var r = this._rnd.NextDouble();
                if (r < 0.55)
                {
                    this.Set("idle", 24 + this._rnd.Next(40));
                }
                else if (r < 0.88)
                {
                    this._targetX = this._rnd.Next(this._minX, this._maxX + 1);
                    if (this._targetX == this._x)
                    {
                        this.Set("idle", 20);
                        return;
                    }
                    this.Set(this._targetX > this._x ? "walk_r" : "walk_l", 200);
                }
                else
                {
                    this.Set("dance", 24 + this._rnd.Next(16));
                }
            }
        }

        private void Set(String state, Int32 ticks)
        {
            if (this._state != state)
            {
                this._frame = 0;
            }
            this._state = state;
            this._ticksLeft = ticks;
        }

        // --- sesje Claude Code -----------------------------------------------------------------------
        // Kazdy plik to ostatnie zdarzenie jednej sesji; stany krotkotrwale wygasaja, "working" po 10 min
        // bez zdarzen (np. Ctrl+C bez Stop), pliki starsze niz doba sa sprzatane.
        private void ReadSessions()
        {
            String best = "idle";
            Int32 working = 0, waiting = 0;
            try
            {
                if (Directory.Exists(this._sessionsDir))
                {
                    var now = DateTimeOffset.UtcNow.ToUnixTimeMilliseconds() / 1000.0;
                    foreach (var file in Directory.EnumerateFiles(this._sessionsDir, "*.json"))
                    {
                        String state;
                        Double age;
                        try
                        {
                            using var doc = JsonDocument.Parse(File.ReadAllText(file));
                            state = doc.RootElement.GetProperty("state").GetString();
                            age = now - doc.RootElement.GetProperty("ts").GetDouble();
                        }
                        catch (Exception)
                        {
                            continue;
                        }
                        if (age > 86400)
                        {
                            try { File.Delete(file); } catch (Exception) { }
                            continue;
                        }
                        var effective = state switch
                        {
                            "attention" => age < 1800 ? "attention" : "idle",
                            "oops" => age < 4 ? "oops" : age < 600 ? "working" : "idle",
                            "compact" => age < 90 ? "compact" : age < 600 ? "working" : "idle",
                            "working" => age < 600 ? "working" : "idle",
                            "done" => age < 6 ? "done" : "idle",
                            "hello" => age < 4 ? "hello" : "idle",
                            _ => "idle",
                        };
                        if (effective is "working" or "compact" or "oops")
                        {
                            working++;
                        }
                        if (effective == "attention")
                        {
                            waiting++;
                        }
                        if (Array.IndexOf(ClaudePriority, effective) > Array.IndexOf(ClaudePriority, best))
                        {
                            best = effective;
                        }
                    }
                }
            }
            catch (Exception)
            {
                // katalog chwilowo niedostepny: zostaw poprzedni stan
                return;
            }
            this._claude = best;
            this._working = working;
            this._waiting = waiting;
        }

        // --- render ----------------------------------------------------------------------------------
        public BitmapImage Render()
        {
            lock (this._lock)
            {
                using var bb = new BitmapBuilder(240, 240);
                bb.Clear(BitmapColor.Black);
                if (!this._frames.TryGetValue(this._state, out var frames) || frames.Length == 0)
                {
                    bb.FillRectangle(70, 100, 100, 50, new BitmapColor(217, 119, 87));
                    return bb.ToImage();
                }
                if (this._floor != null)
                {
                    bb.DrawImage(this._floor, 0, 0, BitmapRotation.None);
                }
                var dx = (this._x - this._center) * this._scale;
                bb.DrawImage(frames[this._frame % frames.Length], dx, 0, BitmapRotation.None);
                if (this._hunger > 85 && this._state != "eat" && this._frame % 8 < 4)
                {
                    // pusty brzuszek: migajacy czerwony punkcik nad glowa
                    bb.FillRectangle(114 + dx, 40, 12, 12, new BitmapColor(232, 64, 64));
                }
                this.DrawSessionDots(bb);
                return bb.ToImage();
            }
        }

        // Kropki na dole ekranu: zolte (migaja) = sesje czekajace na Ciebie, pomaranczowe = sesje w pracy.
        private void DrawSessionDots(BitmapBuilder bb)
        {
            var total = Math.Min(8, this._waiting + this._working);
            if (total == 0)
            {
                return;
            }
            var x0 = 120 - (total - 1) * 9;
            for (var i = 0; i < total; i++)
            {
                var waiting = i < this._waiting;
                if (waiting && this._frame % 6 >= 3)
                {
                    continue;
                }
                var color = waiting ? new BitmapColor(255, 214, 72) : new BitmapColor(217, 119, 87);
                bb.FillCircle(x0 + i * 18, 214, 5, color);
            }
        }
    }
}
