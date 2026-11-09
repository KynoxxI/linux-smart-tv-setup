#!/usr/bin/env python3
import base64
import http.server
import json
import os
import subprocess
import urllib.request

ADB = os.path.expanduser("~/Android/Sdk/platform-tools/adb")

HTML = """<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<title>Télécommande TV</title>
<style>
  * { box-sizing: border-box; user-select: none; -webkit-user-select: none; -webkit-touch-callout: none; }
  body {
    margin: 0; padding: 16px;
    background: #121318; color: #fff;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    display: flex; flex-direction: column; align-items: center; justify-content: space-between;
    min-height: 100vh;
  }
  .tabs {
    display: flex; background: #1e2029; border-radius: 999px; padding: 4px; width: 100%; max-width: 340px;
  }
  .tab {
    flex: 1; text-align: center; padding: 10px 0; border-radius: 999px; font-weight: 600; font-size: 14px;
    color: #9aa0a6; cursor: pointer; transition: 0.2s;
  }
  .tab.active { background: #3b82f6; color: #fff; }
  .dpad {
    position: relative; width: 250px; height: 250px; border-radius: 50%;
    background: #1e2029; box-shadow: 0 10px 30px rgba(0,0,0,0.5), inset 0 2px 4px rgba(255,255,255,0.06);
    margin: 16px 0;
  }
  .dpad button {
    position: absolute; background: transparent; border: none; color: #e8eaed;
    font-size: 26px; display: flex; align-items: center; justify-content: center;
    cursor: pointer; border-radius: 50%;
  }
  .dpad button:active { background: rgba(255,255,255,0.12); }
  .up    { top: 8px; left: 75px; width: 100px; height: 75px; }
  .down  { bottom: 8px; left: 75px; width: 100px; height: 75px; }
  .left  { left: 8px; top: 75px; width: 75px; height: 100px; }
  .right { right: 8px; top: 75px; width: 75px; height: 100px; }
  .ok {
    top: 75px; left: 75px; width: 100px; height: 100px;
    background: #2b2e3b !important; font-weight: 700; font-size: 18px !important;
    box-shadow: 0 4px 12px rgba(0,0,0,0.4), inset 0 1px 2px rgba(255,255,255,0.1);
  }
  .ok:active { background: #3b82f6 !important; }
  .row {
    display: flex; gap: 16px; width: 100%; max-width: 340px; justify-content: center; margin: 6px 0;
  }
  .btn {
    flex: 1; height: 56px; border-radius: 28px; border: none;
    background: #1e2029; color: #e8eaed; font-size: 20px; font-weight: 600;
    display: flex; align-items: center; justify-content: center; gap: 6px;
    box-shadow: 0 4px 10px rgba(0,0,0,0.3); cursor: pointer;
  }
  .btn:active { background: #3b82f6; transform: scale(0.97); }
  .search-box {
    display: flex; gap: 8px; width: 100%; max-width: 340px; margin-top: 8px;
  }
  .search-box input {
    flex: 1; padding: 12px 16px; border-radius: 24px; border: 1px solid #2e3240;
    background: #1e2029; color: #fff; font-size: 15px; outline: none;
  }
  .search-box button {
    padding: 0 18px; border-radius: 24px; border: none; background: #3b82f6; color: #fff; font-weight: 600;
  }
  .status { font-size: 12px; color: #6b7280; margin-top: 4px; }
</style>
</head>
<body>
  <div class="tabs">
    <div class="tab active" onclick="setTarget('both', this)">Les Deux</div>
    <div class="tab" onclick="setTarget('googletv', this)">Google TV</div>
    <div class="tab" onclick="setTarget('kodi', this)">Kodi</div>
  </div>

  <div class="dpad">
    <button class="up" onclick="send('up')">▲</button>
    <button class="down" onclick="send('down')">▼</button>
    <button class="left" onclick="send('left')">◀</button>
    <button class="right" onclick="send('right')">▶</button>
    <button class="ok" onclick="send('ok')">OK</button>
  </div>

  <div class="row">
    <button class="btn" onclick="send('back')">↩ Retour</button>
    <button class="btn" onclick="send('home')">🏠 Accueil</button>
    <button class="btn" onclick="send('menu')">☰ Menu</button>
  </div>

  <div class="row">
    <button class="btn" onclick="send('voldown')">🔉 -</button>
    <button class="btn" onclick="send('mute')">🔇</button>
    <button class="btn" onclick="send('volup')">🔊 +</button>
  </div>

  <div class="row">
    <button class="btn" onclick="send('rw')">⏪</button>
    <button class="btn" onclick="send('playpause')">⏯</button>
    <button class="btn" onclick="send('ff')">⏩</button>
  </div>

  <div class="row">
    <button class="btn" style="background:#e11d48;font-size:15px;" onclick="send('app_movix')">🍿 Movix TV</button>
    <button class="btn" style="background:#dc2626;font-size:15px;" onclick="send('app_smarttube')">▶️ SmartTube</button>
    <button class="btn" style="background:#7c3aed;font-size:15px;" onclick="send('app_stremio')">🎬 Stremio</button>
  </div>

  <div class="row">
    <button class="btn" style="background:#0284c7;font-size:14px;" onclick="send('app_kodi')">📺 Ouvrir Kodi</button>
    <button class="btn" style="background:#059669;font-size:14px;" onclick="send('app_googletv')">📺 Google TV</button>
    <button class="btn" style="background:#374151;font-size:14px;" onclick="send('fullscreen')">🔲 Plein écran</button>
  </div>

  <div class="search-box">
    <input id="txt" type="text" placeholder="Envoyer du texte à l'écran...">
    <button onclick="sendText()">Envoyer</button>
  </div>

  <div class="status" id="st">Connecté à votre PC</div>

<script>
document.getElementById('st').textContent = 'Connecté à votre PC (' + window.location.hostname + ')';
let currentTarget = 'both';
function setTarget(t, el) {
  currentTarget = t;
  document.querySelectorAll('.tab').forEach(x => x.classList.remove('active'));
  el.classList.add('active');
}
function send(cmd) {
  if (navigator.vibrate) navigator.vibrate(15);
  fetch('/api/cmd', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({target: currentTarget, cmd: cmd})
  }).catch(e => {});
}
function sendText() {
  const input = document.getElementById('txt');
  if (!input.value) return;
  fetch('/api/text', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({target: currentTarget, text: input.value})
  }).then(() => { input.value = ''; });
}
</script>
</body>
</html>
"""

ADB_KEYMAP = {
    "up": "KEYCODE_DPAD_UP",
    "down": "KEYCODE_DPAD_DOWN",
    "left": "KEYCODE_DPAD_LEFT",
    "right": "KEYCODE_DPAD_RIGHT",
    "ok": "KEYCODE_DPAD_CENTER",
    "back": "KEYCODE_BACK",
    "home": "KEYCODE_HOME",
    "menu": "KEYCODE_MENU",
    "playpause": "KEYCODE_MEDIA_PLAY_PAUSE",
    "rw": "KEYCODE_MEDIA_REWIND",
    "ff": "KEYCODE_MEDIA_FAST_FORWARD",
    "volup": "KEYCODE_VOLUME_UP",
    "voldown": "KEYCODE_VOLUME_DOWN",
    "mute": "KEYCODE_VOLUME_MUTE",
}

def kodi_rpc(method, params=None):
    payload = {"jsonrpc": "2.0", "method": method, "id": 1}
    if params is not None:
        payload["params"] = params
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request("http://127.0.0.1:8080/jsonrpc", data=data)
    req.add_header("Content-Type", "application/json")
    b64 = base64.b64encode(b"kodi:kodi").decode("ascii")
    req.add_header("Authorization", f"Basic {b64}")
    try:
        urllib.request.urlopen(req, timeout=1)
    except Exception:
        pass

class RemoteHandler(http.server.BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass

    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(HTML.encode("utf-8"))

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        body = json.loads(self.rfile.read(length).decode("utf-8"))
        target = body.get("target", "both")

        if self.path == "/api/cmd":
            cmd = body.get("cmd", "")
            # System volume & App launchers for PC
            if cmd == "volup":
                subprocess.Popen(["wpctl", "set-volume", "@DEFAULT_AUDIO_SINK@", "5%+"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            elif cmd == "voldown":
                subprocess.Popen(["wpctl", "set-volume", "@DEFAULT_AUDIO_SINK@", "5%-"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            elif cmd == "mute":
                subprocess.Popen(["wpctl", "set-mute", "@DEFAULT_AUDIO_SINK@", "toggle"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            elif cmd == "app_kodi":
                subprocess.Popen(["flatpak", "run", "tv.kodi.Kodi"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)
            elif cmd == "app_googletv":
                emu = os.path.expanduser("~/Android/Sdk/emulator/emulator")
                subprocess.Popen([emu, "-avd", "Google_TV_1080p", "-gpu", "host"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)
            elif cmd == "fullscreen":
                kodi_rpc("GUI.SetFullscreen", {"fullscreen": "toggle"})

            # Google TV (ADB)
            if cmd == "app_movix":
                subprocess.Popen([ADB, "shell", "am", "start", "-n", "com.movix.tv/.MainActivity"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            elif cmd == "app_smarttube":
                subprocess.Popen([ADB, "shell", "monkey", "-p", "org.smarttube.stable", "-c", "android.intent.category.LEANBACK_LAUNCHER", "1"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                subprocess.Popen([ADB, "shell", "monkey", "-p", "com.liskovsoft.smarttubetv.beta", "1"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            elif cmd == "app_stremio":
                subprocess.Popen([ADB, "shell", "monkey", "-p", "com.stremio.one", "-c", "android.intent.category.LEANBACK_LAUNCHER", "1"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            elif target in ("both", "googletv") and cmd in ADB_KEYMAP:
                subprocess.Popen([ADB, "shell", "input", "keyevent", ADB_KEYMAP[cmd]], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

            # Kodi (JSON-RPC)
            if target in ("both", "kodi"):
                kodi_map = {
                    "up": ("Input.Up", None),
                    "down": ("Input.Down", None),
                    "left": ("Input.Left", None),
                    "right": ("Input.Right", None),
                    "ok": ("Input.Select", None),
                    "back": ("Input.Back", None),
                    "home": ("Input.Home", None),
                    "menu": ("Input.ContextMenu", None),
                    "playpause": ("Player.PlayPause", {"playerid": 1}),
                    "rw": ("Player.Seek", {"playerid": 1, "value": {"seconds": -10}}),
                    "ff": ("Player.Seek", {"playerid": 1, "value": {"seconds": 10}}),
                }
                if cmd in kodi_map:
                    m, p = kodi_map[cmd]
                    kodi_rpc(m, p)

        elif self.path == "/api/text":
            text = body.get("text", "")
            if target in ("both", "googletv") and text:
                escaped = text.replace(" ", "%s")
                subprocess.Popen([ADB, "shell", "input", "text", escaped], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            if target in ("both", "kodi") and text:
                kodi_rpc("Input.SendText", {"text": text, "done": True})

        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(b'{"ok":true}')

if __name__ == "__main__":
    server = http.server.ThreadingHTTPServer(("0.0.0.0", 8888), RemoteHandler)
    print("Serveur Télécommande TV actif sur http://192.168.1.27:8888")
    server.serve_forever()
