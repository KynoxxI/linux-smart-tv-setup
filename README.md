# 📺 Linux Smart TV Suite (Google TV + Movix TV + Kodi + Stremio + Télécommande Web iPhone)

Ce dépôt permet de transformer n'importe quel PC Linux (**Fedora**, **Ubuntu/Debian/Mint**, **Arch Linux**) en une véritable **Smart TV / Fire Stick / Google TV** en une seule commande.

## ✨ Ce qui est inclus et installé automatiquement

1. **Émulateur officiel Google TV (1080p)** pré-équipé avec :
   - 🍿 **Movix TV** (Films, Séries et Animes en VF / VOSTFR)
   - ▶️ **SmartTube** (YouTube TV sans publicité + SponsorBlock intégré)
   - Raccourci **« Google TV (Émulateur 1080p) »** dans le menu d'applications du PC.
2. **Télécommande Web TV universelle (`tv_remote_server.py`)** :
   - Tourne automatiquement en tâche de fond (`systemd --user` sur le port `8888`).
   - Accessible depuis **Safari / Chrome sur votre iPhone ou Android** sans aucune application à installer (`http://<IP_DU_PC>:8888`).
   - Contrôle **Google TV**, **Kodi** et le **volume du PC**, avec boutons directs pour lancer **Movix TV**, **SmartTube**, **Stremio** et **Kodi**.
3. **Kodi (Flatpak) pré-configuré** :
   - Contrôle à distance HTTP (`8080`, identifiants `kodi` / `kodi`), **AirPlay** et **UPnP / DLNA** déjà activés (`config/advancedsettings.xml`, `config/guisettings.xml`, `config/sources.xml`).
   - Dépôts `.zip` prêts à l'emploi copiés automatiquement dans `~/Vidéos/Kodi-Addons` :
     - `0-TOUT-EN-UN-vStream-Repo.zip` (**vStream** : Films, Séries, Animes VF/VOSTFR)
     - `1-Netflix-CastagnaIT-Repo.zip` (**Netflix**)
     - `2-DisneyPlus-PlutoTV-SlyGuy-Repo.zip` (**Disney+, Max, Paramount+, Pluto TV, Samsung TV Plus**)
     - `3-PrimeVideo-Sandmann79-Repo.zip` (**Amazon Prime Video**)
     - `4-YouTube-Addon.zip` (**YouTube pour Kodi**)
     - `5-Theme-Netflix-GoogleTV-ArcticFuse-Repo.zip` (**Thème Netflix / Google TV Arctic Fuse**)
4. **Stremio** (Flatpak) & **KDE Connect**.

---

## 🚀 Installation sur un autre PC (en 1 commande)

Ouvrez un terminal sur le nouveau PC et lancez :

```bash
git clone https://github.com/KynoxxI/linux-smart-tv-setup.git ~/TV-Setup
cd ~/TV-Setup
chmod +x install.sh
./install.sh
```

