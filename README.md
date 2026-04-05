# BrowseIt 🧭

A Blender addon that lets you quickly navigate to your favorite N-Panel tabs via a pie menu and a search popup.

![Blender](https://img.shields.io/badge/Blender-4.0%2B-orange?logo=blender&logoColor=white)
![License](https://img.shields.io/badge/License-GPL--3.0--or--later-blue)
![Version](https://img.shields.io/badge/Version-1.0.2-green)

---

## ✨ Features

| Feature | Shortcut | Description |
|---|---|---|
| **Favorites Pie Menu** | `Alt + Q` | Instantly jump to any of 8 assigned N-Panel tabs |
| **Search All Tabs** | `Alt + Shift + Q` | Fuzzy-search through every registered N-Panel tab |
| **Search & Add to Pie** | `Alt + Ctrl + Q` | Search for a tab and assign it to a pie slot |
| **Reassign Slot** | `Ctrl + Click` (pie) | Ctrl+Click any pie slot to reassign it via search |
| **Slot Assignment** | *Addon Preferences* | Assign any N-Panel tab to one of 8 directional pie slots |

- 🔍 **Smart Detection** — Automatically discovers all N-Panel tabs from installed addons
- ⚡ **One-Key Access** — Open sidebar and switch tabs in a single shortcut
- 🎯 **8 Pie Slots** — Map your most-used tabs to directional positions (N, S, E, W, NE, NW, SE, SW)
- 🔄 **Quick Reassign** — Ctrl+Click any pie slot to swap it, or click an empty slot to assign
- 📋 **Assignment Overview** — Slot picker dialog shows all current assignments at a glance

---

## 📦 Installation

1. Download the [latest release](../../releases/latest) (`.zip` file).
2. In Blender go to **Edit → Preferences → Add-ons → Install…**
3. Select the downloaded `.zip` and click **Install Add-on**.
4. Enable **BrowseIt** in the addon list.

> [!TIP]
> You can also clone this repo directly into your Blender addons folder:
> ```
> cd %APPDATA%\Blender Foundation\Blender\4.2\scripts\addons
> git clone https://github.com/<your-username>/BrowseIt.git
> ```

---

## 🚀 Usage

### Pie Menu (`Alt + Q`)

Press **Alt + Q** in the 3D Viewport to open the pie menu. Each of the 8 slots can be mapped to a different N-Panel tab in the addon preferences.

- **Click** a slot → jump to that N-Panel tab
- **Ctrl + Click** a slot → search popup to reassign that slot
- **Click an empty slot** → search popup to assign a tab to it

### Search (`Alt + Shift + Q`)

Press **Alt + Shift + Q** to open a search popup. Start typing to filter through all available N-Panel tabs, then select one to jump directly to it.

### Search & Add to Pie (`Alt + Ctrl + Q`)

Press **Alt + Ctrl + Q** to search for a tab and assign it to a pie slot. The slot picker dialog shows all current assignments so you can see which slots are taken and which are empty.

### Configuring Slots

1. Go to **Edit → Preferences → Add-ons**
2. Find **BrowseIt** and expand its preferences
3. Assign your favourite N-Panel tabs to each of the 8 directional slots

---

## 🖼️ Screenshots

<!-- Add screenshots here once available -->
<!-- ![Pie Menu](docs/images/pie_menu.png) -->
<!-- ![Search Popup](docs/images/search_popup.png) -->

---

## 🔧 Compatibility

| Requirement | Version |
|---|---|
| Blender | **4.0** or newer |
| Python | Bundled with Blender |

---

## 📄 License

This project is licensed under the **GNU General Public License v3.0 or later**.  
See the [LICENSE](LICENSE) file for details.

---

## 🤝 Contributing

Contributions are welcome! Feel free to:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m "Add amazing feature"`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📝 Changelog

See [CHANGELOG.md](CHANGELOG.md) for a list of changes.

---

## 🙏 Acknowledgments

- Built with the [Blender Python API](https://docs.blender.org/api/current/)
