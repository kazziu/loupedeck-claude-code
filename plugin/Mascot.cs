namespace Loupedeck.ClaudeMascotPlugin
{
    using System;
    using System.Collections.Generic;
    using System.IO;
    using System.Reflection;
    using System.Text.Json;
    using System.Threading;

    // Tamagotchi: stan, statystyki i skladanie klatek (pixel art z art/pixelart.py -> frames/*.png).
    internal sealed class Mascot : IDisposable
    {
        private const Int32 TickMs = 120;
        private static readonly TimeSpan SleepAfter = TimeSpan.FromMinutes(3);
        private static readonly TimeSpan FullHungerAfter = TimeSpan.FromMinutes(45);

        private readonly Object _lock = new();
        private readonly Random _rnd = new();
        private readonly Dictionary<String, BitmapImage[]> _frames = new();
        private readonly String _stateFile;
        private BitmapImage _floor;
        private Int32 _scale = 5, _minX = 18, _maxX = 30;
        private Timer _timer;

        private String _state = "idle";
        private Int32 _frame, _ticksLeft, _x = 24, _targetX = 24;
        private Double _hunger = 20, _spin;
        private DateTime _lastTouch = DateTime.Now;
        private Boolean _claudeWorking;
        private Int32 _stateFileCheck;

        public event Action Changed;

        public Mascot(Assembly assembly)
        {
            this._stateFile = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.UserProfile),
                ".config", "loupedeck-cc", "claude-state");
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
                this._lastTouch = DateTime.Now;
                if (this._state == "sleep")
                {
                    this.Set("happy", 16);                 // obudzony, ale zadowolony
                }
                else if (this._hunger > 40)
                {
                    this._hunger = 0;
                    this.Set("eat", 16 * 2);              // dwie porcje chrupania
                }
                else
                {
                    this.Set(this._rnd.Next(2) == 0 ? "pet" : "happy", 16);
                }
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
                    this.Set("dizzy", 30);
                }
                else if (this._state == "sleep")
                {
                    this.Set("idle", 10);
                }
            }
        }

        // --- petla -----------------------------------------------------------------------------------
        private void Tick()
        {
            lock (this._lock)
            {
                this._frame++;
                this._spin *= 0.85;
                this._hunger = Math.Min(100, this._hunger + 100.0 * TickMs / FullHungerAfter.TotalMilliseconds);
                if (++this._stateFileCheck % 16 == 0)
                {
                    this._claudeWorking = this.ReadClaudeWorking();
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
            this.Changed?.Invoke();
        }

        private void ChooseNext()
        {
            var bored = DateTime.Now - this._lastTouch;
            if (this._claudeWorking)
            {
                this.Set("work", 25);
            }
            else if (bored > SleepAfter)
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

        // Plik ~/.config/loupedeck-cc/claude-state ("working"/"idle") moga zapisywac hooki Claude Code.
        private Boolean ReadClaudeWorking()
        {
            try
            {
                var fi = new FileInfo(this._stateFile);
                return fi.Exists && DateTime.Now - fi.LastWriteTime < TimeSpan.FromMinutes(10)
                    && File.ReadAllText(fi.FullName).Trim() == "working";
            }
            catch (Exception)
            {
                return false;
            }
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
                bb.DrawImage(frames[this._frame % frames.Length], (this._x - 24) * this._scale, 0, BitmapRotation.None);
                if (this._hunger > 85 && this._state != "eat")
                {
                    // pusty brzuszek: migajacy czerwony punkcik nad glowa
                    if (this._frame % 8 < 4)
                    {
                        bb.FillRectangle(115 + (this._x - 24) * this._scale, 60, 10, 10, new BitmapColor(232, 64, 64));
                    }
                }
                return bb.ToImage();
            }
        }
    }
}
