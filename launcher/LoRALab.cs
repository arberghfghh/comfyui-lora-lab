// LoRA Lab launcher for Windows (optional — LoRA Lab also works by opening its address in any browser).
//
// Opens LoRA Lab in its own app window. If ComfyUI isn't running yet, it tries to start it in the background
// and stops it again when the window closes. Settings (all optional) go in LoRALab.json next to this exe:
//   {
//     "url": "http://127.0.0.1:8188",          // where ComfyUI runs
//     "comfyui_folder": "D:\\ComfyUI",          // folder containing main.py (portable or manual install)
//     "python": "D:\\ComfyUI\\venv\\Scripts\\python.exe",  // optional, otherwise detected
//     "extra_args": "",                         // e.g. "--lowvram"
//     "listen_on_network": false                // true = other devices on your network can connect (no password!)
//   }
//
// Build (C# 5 / .NET Framework 4, included with Windows):
//   C:\Windows\Microsoft.NET\Framework64\v4.0.30319\csc.exe /nologo /codepage:65001 /target:winexe ^
//     /win32icon:LoRALab.ico /r:System.Windows.Forms.dll /r:System.Drawing.dll /r:System.Core.dll ^
//     /r:System.Web.Extensions.dll /out:LoRALab.exe LoRALab.cs
using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Drawing;
using System.IO;
using System.Linq;
using System.Net;
using System.Threading;
using System.Web.Script.Serialization;
using System.Windows.Forms;

static class Program
{
    const int StartTimeoutSeconds = 300;
    static readonly string LocalAppData = Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData);
    static readonly string RoamingAppData = Environment.GetFolderPath(Environment.SpecialFolder.ApplicationData);
    static readonly string DataDir = Path.Combine(LocalAppData, "LoRA Lab");
    static readonly string LogPath = Path.Combine(DataDir, "comfyui-server.log");
    static readonly string ExeDir = Path.GetDirectoryName(Application.ExecutablePath);

    static string BaseUrl = "http://127.0.0.1:8188";
    static string ComfyFolder = "", PythonPath = "", ExtraArgs = "";
    static bool ListenOnNetwork = false;

    [STAThread]
    static void Main()
    {
        Application.EnableVisualStyles();
        Application.SetCompatibleTextRenderingDefault(false);
        Directory.CreateDirectory(DataDir);
        LoadConfig();

        bool firstInstance;
        using (var mutex = new Mutex(true, "LoRALab.Launcher", out firstInstance))
        {
            if (!firstInstance) { OpenAppWindow(); return; }

            Process server = null;
            if (!IsUp(BaseUrl + "/system_stats"))
            {
                server = StartComfyServer();
                if (server == null) return;
                if (!WaitWithSplash(server)) { KillTree(server); return; }
            }
            if (!IsUp(BaseUrl + "/lora-lab"))
            {
                MessageBox.Show("ComfyUI is running, but the LoRA Lab custom node isn't loaded.\n\n" +
                    "Put the comfyui-lora-lab folder in ComfyUI's custom_nodes folder and restart ComfyUI.",
                    "LoRA Lab", MessageBoxButtons.OK, MessageBoxIcon.Warning);
                if (server != null) KillTree(server);
                return;
            }

            Process window = OpenAppWindow();
            if (window != null) window.WaitForExit();
            else if (server != null)
                MessageBox.Show("LoRA Lab is open in your browser. Click OK when you're done to stop the background ComfyUI server.",
                    "LoRA Lab", MessageBoxButtons.OK, MessageBoxIcon.Information);
            if (server != null) KillTree(server);
        }
    }

    static void LoadConfig()
    {
        string path = Path.Combine(ExeDir, "LoRALab.json");
        if (!File.Exists(path)) return;
        try
        {
            // Allow // comments in the config file.
            string text = string.Join("\n", File.ReadAllLines(path).Select(l => l.Trim().StartsWith("//") ? "" : l));
            var cfg = new JavaScriptSerializer().Deserialize<Dictionary<string, object>>(text);
            object v;
            if (cfg.TryGetValue("url", out v) && v != null) BaseUrl = v.ToString().TrimEnd('/');
            if (cfg.TryGetValue("comfyui_folder", out v) && v != null) ComfyFolder = v.ToString();
            if (cfg.TryGetValue("python", out v) && v != null) PythonPath = v.ToString();
            if (cfg.TryGetValue("extra_args", out v) && v != null) ExtraArgs = v.ToString();
            if (cfg.TryGetValue("listen_on_network", out v) && v is bool) ListenOnNetwork = (bool)v;
        }
        catch (Exception e)
        {
            MessageBox.Show("Couldn't read LoRALab.json: " + e.Message, "LoRA Lab", MessageBoxButtons.OK, MessageBoxIcon.Warning);
        }
    }

    static bool IsUp(string url)
    {
        try
        {
            var req = (HttpWebRequest)WebRequest.Create(url);
            req.Timeout = 1500; req.Proxy = null;
            using (var resp = (HttpWebResponse)req.GetResponse()) return resp.StatusCode == HttpStatusCode.OK;
        }
        catch { return false; }
    }

    class ComfyInstall { public string Python, WorkDir, Args; }

    // Finds a ComfyUI to start: LoRALab.json, then Comfy Desktop, then a portable folder next to the launcher.
    static ComfyInstall FindComfy()
    {
        var candidates = new List<string>();
        if (ComfyFolder != "") candidates.Add(ComfyFolder);
        string desktopInstalls = Path.Combine(LocalAppData, @"Comfy-Desktop\ComfyUI-Installs");
        if (Directory.Exists(desktopInstalls))
            candidates.AddRange(new DirectoryInfo(desktopInstalls).GetDirectories()
                .OrderByDescending(d => d.LastWriteTime).Select(d => Path.Combine(d.FullName, "ComfyUI")));
        candidates.Add(Path.Combine(ExeDir, "ComfyUI"));
        candidates.Add(Path.Combine(ExeDir, @"..\ComfyUI"));

        foreach (string folder in candidates)
        {
            if (!File.Exists(Path.Combine(folder, "main.py"))) continue;
            string py = PythonPath;
            if (py == "" || !File.Exists(py))
            {
                string[] options = {
                    Path.Combine(folder, @".venv\Scripts\python.exe"), Path.Combine(folder, @"venv\Scripts\python.exe"),
                    Path.Combine(folder, @"..\python_embeded\python.exe") };
                py = options.FirstOrDefault(File.Exists) ?? "python";
            }
            var inst = new ComfyInstall { Python = py, WorkDir = folder, Args = "-s main.py" };

            // Comfy Desktop keeps models and outputs in a shared folder next to its installs.
            string shared = Path.GetFullPath(Path.Combine(folder, @"..\..\..\ComfyUI-Shared"));
            if (folder.StartsWith(desktopInstalls, StringComparison.OrdinalIgnoreCase) && Directory.Exists(shared))
            {
                inst.Args += " --input-directory \"" + Path.Combine(shared, "input") + "\" --output-directory \"" + Path.Combine(shared, "output") + "\"";
                string paths = Path.Combine(RoamingAppData, @"Comfy Desktop\instance-model-paths");
                if (Directory.Exists(paths))
                {
                    var yaml = new DirectoryInfo(paths).GetFiles("*.yaml").OrderByDescending(f => f.LastWriteTime).FirstOrDefault();
                    if (yaml != null) inst.Args += " --extra-model-paths-config \"" + yaml.FullName + "\"";
                }
            }
            return inst;
        }
        return null;
    }

    static Process StartComfyServer()
    {
        var inst = FindComfy();
        if (inst == null)
        {
            MessageBox.Show("ComfyUI isn't running and I couldn't find it to start it.\n\n" +
                "Start ComfyUI yourself and open LoRA Lab again, or set \"comfyui_folder\" in LoRALab.json " +
                "(next to LoRALab.exe) to the folder that contains ComfyUI's main.py.",
                "LoRA Lab", MessageBoxButtons.OK, MessageBoxIcon.Information);
            return null;
        }
        var uri = new Uri(BaseUrl);
        string args = inst.Args + " --port " + uri.Port + (ListenOnNetwork ? " --listen 0.0.0.0" : "") + (ExtraArgs != "" ? " " + ExtraArgs : "");
        var psi = new ProcessStartInfo(inst.Python, args)
        {
            WorkingDirectory = inst.WorkDir, UseShellExecute = false, CreateNoWindow = true,
            RedirectStandardOutput = true, RedirectStandardError = true,
        };
        psi.EnvironmentVariables["PYTHONIOENCODING"] = "utf-8";
        psi.EnvironmentVariables["PYTHONUTF8"] = "1";

        var log = new StreamWriter(LogPath, false) { AutoFlush = true };
        log.WriteLine("[LoRA Lab] " + DateTime.Now + "  " + inst.Python + " " + args + "  (in " + inst.WorkDir + ")");
        var p = new Process { StartInfo = psi, EnableRaisingEvents = true };
        DataReceivedEventHandler write = (s, e) => { if (e.Data != null) lock (log) log.WriteLine(e.Data); };
        p.OutputDataReceived += write; p.ErrorDataReceived += write;
        try { p.Start(); }
        catch (Exception e)
        {
            MessageBox.Show("Couldn't start ComfyUI with " + inst.Python + ":\n" + e.Message, "LoRA Lab", MessageBoxButtons.OK, MessageBoxIcon.Error);
            return null;
        }
        p.BeginOutputReadLine(); p.BeginErrorReadLine();
        return p;
    }

    static bool WaitWithSplash(Process server)
    {
        bool ready = false, failed = false;
        var form = new Form
        {
            Text = "LoRA Lab", FormBorderStyle = FormBorderStyle.FixedDialog, StartPosition = FormStartPosition.CenterScreen,
            ClientSize = new Size(380, 120), MaximizeBox = false, BackColor = Color.FromArgb(23, 26, 33), ForeColor = Color.FromArgb(230, 232, 238),
        };
        try { form.Icon = Icon.ExtractAssociatedIcon(Application.ExecutablePath); } catch { }
        form.Controls.AddRange(new Control[] {
            new Label { Text = "Starting ComfyUI…", Font = new Font("Segoe UI", 11f, FontStyle.Bold), AutoSize = true, Location = new Point(18, 16) },
            new Label { Text = "This can take a minute. LoRA Lab opens by itself.", Font = new Font("Segoe UI", 9f), ForeColor = Color.FromArgb(139, 147, 165), AutoSize = true, Location = new Point(19, 44) },
            new ProgressBar { Style = ProgressBarStyle.Marquee, MarqueeAnimationSpeed = 25, Location = new Point(20, 78), Size = new Size(340, 14) },
        });
        var watcher = new Thread(() =>
        {
            var sw = Stopwatch.StartNew();
            while (sw.Elapsed.TotalSeconds < StartTimeoutSeconds)
            {
                if (server.HasExited) { failed = true; break; }
                if (IsUp(BaseUrl + "/system_stats")) { ready = true; break; }
                Thread.Sleep(1000);
            }
            if (!ready) failed = true;
            try { form.BeginInvoke(new Action(form.Close)); } catch { }
        }) { IsBackground = true };
        form.Shown += (s, e) => watcher.Start();
        form.ShowDialog();
        if (!ready && failed)
            MessageBox.Show("ComfyUI didn't start.\n\nDetails are in:\n" + LogPath, "LoRA Lab", MessageBoxButtons.OK, MessageBoxIcon.Error);
        return ready;
    }

    // Chrome/Edge in app mode with LoRA Lab's own profile, so the window is a separate app.
    static Process OpenAppWindow()
    {
        string url = BaseUrl + "/lora-lab";
        string pf = Environment.GetFolderPath(Environment.SpecialFolder.ProgramFiles);
        string pf86 = Environment.GetFolderPath(Environment.SpecialFolder.ProgramFilesX86);
        string[] browsers = {
            Path.Combine(pf, @"Google\Chrome\Application\chrome.exe"), Path.Combine(pf86, @"Google\Chrome\Application\chrome.exe"),
            Path.Combine(LocalAppData, @"Google\Chrome\Application\chrome.exe"),
            Path.Combine(pf86, @"Microsoft\Edge\Application\msedge.exe"), Path.Combine(pf, @"Microsoft\Edge\Application\msedge.exe"),
        };
        string browser = browsers.FirstOrDefault(File.Exists);
        if (browser == null) { Process.Start(url); return null; }
        string args = "--app=" + url + " --user-data-dir=\"" + Path.Combine(DataDir, "window-profile") + "\" --no-first-run --no-default-browser-check --window-size=1500,950";
        return Process.Start(new ProcessStartInfo(browser, args) { UseShellExecute = false });
    }

    static void KillTree(Process p)
    {
        try
        {
            if (p.HasExited) return;
            var kill = Process.Start(new ProcessStartInfo("taskkill", "/PID " + p.Id + " /T /F") { CreateNoWindow = true, UseShellExecute = false });
            kill.WaitForExit(10000);
        }
        catch { }
    }
}
