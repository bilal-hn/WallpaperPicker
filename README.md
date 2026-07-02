# Wallpaper Picker

A sleek, lightweight GTK 4-based wallpaper picker designed for Linux. It features smooth async image caching and an instantaneous visual preview. The application is built to run on **Linux Mint (Cinnamon)** and other **Debian-based distributions** using the Cinnamon desktop environment out of the box, with minimal adjustments required for other window managers or desktops.

---

## 📸 Preview

| Application View |
| :---: |
| <img src="screenshots/preview.png" width="600" alt="Wallpaper Picker Interface"> |

---

## ✨ Features

- **Asynchronous Cache System:** Thumbnails and previews load in background threads to avoid UI stutter or freezing.
- **Crossfade Transitions:** Smooth transitions between background selections using Cairo rendering.
- **Single Instance Control:** File locking mechanism preventing multiple instances of the utility from launching simultaneously.
- **Keyboard Navigation:** Full support for `Arrow keys` to navigate, `Enter` to confirm, and `Escape` to close.
- **Dynamic Positioning:** Automatically reads screen boundaries using GDK and positions itself as a dynamic dock using `wmctrl`.

---

## 🛠️ Requirements & Dependencies

The application relies on GTK 4, Python GObject bindings (`PyGObject`), Cairo, and `wmctrl` for desktop integration.

### Install Dependencies on Debian / Ubuntu / Linux Mint

Open your terminal and run the following command to grab all system requirements:

```bash
sudo apt update
sudo apt install python3-gi python3-gi-cairo gir1.2-gtk-4.0 wmctrl
