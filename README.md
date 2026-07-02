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
```

### Compatibility Note (Other Linux Distributions)

While built and optimized for Debian/Ubuntu ecosystems, this app can run on other distributions if you install their equivalent packages:

- **Fedora:** `sudo dnf install python3-gobject gtk4 wmctrl`
- **Arch Linux:** `sudo pacman -S python-gobject gtk4 wmctrl`

> ⚠️ **Desktop Environment Warning:** This script modifies the desktop background using the Cinnamon `gsettings` schema (`org.cinnamon.desktop.background`). If you run standard GNOME (e.g., default Ubuntu), change all occurrences of `org.cinnamon.desktop.background` to `org.gnome.desktop.background` inside the Python file.

---

## 🚀 Installation & Usage

1. **Clone the repository:**

```bash
   git clone https://github.com/bilal-hn/WallpaperPicker.git
   cd WallpaperPicker
```

2. **Make the script executable:**

```bash
   chmod +x wallpaper_picker.py
```

3. **Launch the picker:**

```bash
   ./wallpaper_picker.py
```

---

## 🖼️ Wallpaper Folder Setup

By default, the app looks for images in `~/Pictures/Wallpapers`. Create this folder and place your wallpaper images inside it:

```bash
mkdir -p ~/Pictures/Wallpapers
```

If you'd rather store your wallpapers somewhere else (e.g. a different folder or drive), you'll need to update the path inside `wallpaper_picker.py` to point to your custom location instead.

---

## 📂 Project Structure

```text
WallpaperPicker/
├── wallpaper_picker.py    # Main application executable script
├── style.css              # GTK 4 style rules for layout/theming
├── .wallpaper_picker.lock # Automatic system file (Generated at runtime)
├── .gitignore             # Tells Git to skip indexing the lock file
└── screenshots/           # Directory where you store project images
```

---

## 📝 License

This project is open-source. Feel free to modify, distribute, and tailor it to your personal workflow.
