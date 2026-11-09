#!/usr/bin/env bash
set -e

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
echo "=========================================================="
echo " 📺 Installation complète PC -> Smart TV (Google TV + Kodi)"
echo "=========================================================="

# 1. Installation de KDE Connect & Flatpak selon la distribution
if command -v dnf >/dev/null 2>&1; then
    echo "[1/6] Détection de Fedora : vérification de kde-connect et flatpak..."
    rpm -q kde-connect >/dev/null 2>&1 || sudo dnf install -y kde-connect
    rpm -q flatpak >/dev/null 2>&1 || sudo dnf install -y flatpak
elif command -v apt >/dev/null 2>&1; then
    echo "[1/6] Détection de Ubuntu/Debian : installation de kdeconnect et flatpak..."
    sudo apt update && sudo apt install -y kdeconnect flatpak curl unzip python3
elif command -v pacman >/dev/null 2>&1; then
    echo "[1/6] Détection de Arch Linux : installation de kdeconnect et flatpak..."
    sudo pacman -S --needed --noconfirm kdeconnect flatpak curl unzip python3
fi

# 2. Installation de Kodi et Stremio via Flatpak
echo "[2/6] Installation de Kodi et Stremio via Flathub..."
flatpak remote-add --if-not-exists flathub https://dl.flathub.org/repo/flathub.flatpakrepo
flatpak install -y flathub tv.kodi.Kodi com.stremio.Stremio

# 3. Configuration de Kodi et copie des dépôts (.zip)
echo "[3/6] Pré-configuration de Kodi (Contrôle à distance, AirPlay, UPnP, Dépôts)..."
KODI_DATA="$HOME/.var/app/tv.kodi.Kodi/data"
mkdir -p "$KODI_DATA/userdata" "$KODI_DATA/repos"
cp -f "$REPO_DIR/config/advancedsettings.xml" "$KODI_DATA/userdata/advancedsettings.xml"
cp -f "$REPO_DIR/config/sources.xml" "$KODI_DATA/userdata/sources.xml"
if [ ! -f "$KODI_DATA/userdata/guisettings.xml" ]; then
    cp -f "$REPO_DIR/config/guisettings.xml" "$KODI_DATA/userdata/guisettings.xml"
fi

VIDEOS_DIR="$(xdg-user-dir VIDEOS 2>/dev/null || echo "$HOME/Vidéos")/Kodi-Addons"
mkdir -p "$VIDEOS_DIR"
cp -f "$REPO_DIR"/*.zip "$KODI_DATA/repos/" 2>/dev/null || true
cp -f "$REPO_DIR"/*.zip "$VIDEOS_DIR/" 2>/dev/null || true

# 4. Installation de l'émulateur Google TV 1080p + Movix TV + SmartTube + Stremio TV
echo "[4/6] Installation du SDK Android et création de l'émulateur Google TV 1080p..."
if [ ! -f "$HOME/.local/bin/android" ]; then
    curl -fsSL https://dl.google.com/android/cli/latest/linux_x86_64/install.sh | bash
fi

ANDROID_BIN="$HOME/.local/bin/android"
"$ANDROID_BIN" sdk install emulator platform-tools platforms/android-34 system-images/android-34/google-tv/x86 cmdline-tools/latest

SDK_DIR="$HOME/Android/Sdk"
AVDMANAGER="$SDK_DIR/cmdline-tools/latest/bin/avdmanager"
EMULATOR_BIN="$SDK_DIR/emulator/emulator"
ADB_BIN="$SDK_DIR/platform-tools/adb"

echo "no" | "$AVDMANAGER" create avd -n Google_TV_1080p -k "system-images;android-34;google-tv;x86" -d "tv_1080p" --force
CONFIG_INI="$HOME/.android/avd/Google_TV_1080p.avd/config.ini"
if [ -f "$CONFIG_INI" ]; then
    grep -q "hw.keyboard = yes" "$CONFIG_INI" || printf "\nhw.keyboard = yes\nhw.dPad = yes\nhw.ramSize = 4096\n" >> "$CONFIG_INI"
fi

mkdir -p "$HOME/.local/share/applications"
cat > "$HOME/.local/share/applications/google-tv-emulator.desktop" <<EOF
[Desktop Entry]
Name=Google TV (Émulateur 1080p)
Comment=Lancer Google TV complet avec Movix TV et SmartTube
Exec=$EMULATOR_BIN -avd Google_TV_1080p -gpu host
Icon=tv.kodi.Kodi
Terminal=false
Type=Application
Categories=AudioVideo;Video;TV;
EOF
chmod +x "$HOME/.local/share/applications/google-tv-emulator.desktop"

# 5. Téléchargement et installation de Movix TV & SmartTube dans Google TV
echo "[5/6] Téléchargement de Movix TV et SmartTube dans Google TV..."
APK_DIR="$REPO_DIR/apks"
mkdir -p "$APK_DIR"
curl -fsSL "https://raw.githubusercontent.com/movixstream/MovixOpenSource/main/app-tv/movix-tv.apk" -o "$APK_DIR/movix-tv.apk"
SMARTTUBE_URL=$(curl -fsSL https://api.github.com/repos/yuliskov/SmartTube/releases/latest | grep -o 'https://[^"]*universal\.apk' | head -n 1)
if [ -n "$SMARTTUBE_URL" ]; then
    curl -fsSL "$SMARTTUBE_URL" -o "$APK_DIR/SmartTube.apk"
fi

nohup "$EMULATOR_BIN" -avd Google_TV_1080p -gpu host >/dev/null 2>&1 &
"$ADB_BIN" wait-for-device
for _ in $(seq 1 90); do
    if [ "$("$ADB_BIN" shell getprop sys.boot_completed 2>/dev/null | tr -d '\r')" = "1" ]; then
        break
    fi
    sleep 2
done
sleep 3
"$ADB_BIN" install -r "$APK_DIR/movix-tv.apk" || true
[ -f "$APK_DIR/SmartTube.apk" ] && "$ADB_BIN" install -r "$APK_DIR/SmartTube.apk" || true
"$ADB_BIN" shell am start -n com.movix.tv/.MainActivity || true

# 6. Activation du serveur Télécommande Web TV pour iPhone / Smartphone (port 8888)
echo "[6/6] Activation du service Télécommande Web TV (port 8888)..."
chmod +x "$REPO_DIR/tv_remote_server.py"
mkdir -p "$HOME/.config/systemd/user"
cat > "$HOME/.config/systemd/user/tv-remote.service" <<EOF
[Unit]
Description=Télécommande Web TV pour Smartphone (Google TV + Kodi + PC)
After=network.target

[Service]
ExecStart=/usr/bin/python3 $REPO_DIR/tv_remote_server.py
Restart=always
RestartSec=2

[Install]
WantedBy=default.target
EOF

systemctl --user daemon-reload
systemctl --user enable --now tv-remote.service

LOCAL_IP=$(hostname -I | awk '{print $1}')
echo "=========================================================="
echo " ✅ Installation terminée avec succès !"
echo " 📱 Télécommande Web TV : http://${LOCAL_IP}:8888"
echo " 📡 Serveur Kodi Remote : ${LOCAL_IP}:8080 (kodi / kodi)"
echo "=========================================================="

