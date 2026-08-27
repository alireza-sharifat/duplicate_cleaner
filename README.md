```markdown
# 🧹 Duplicate Cleaner – Find & Remove Duplicate and Empty Files

Stop wasting disk space on duplicate files and useless zero‑byte clutter. Duplicate Cleaner is a powerful Windows/Linux/macOS application that scans your folders or entire system, detects duplicate files based on **actual content** (not just file names), and removes them with a single click. It also automatically deletes **all empty files** – leaving your drive clean and organized.

No more manual searching, no more guessing – just pure, efficient file management.

---

## ✨ Features

- 🔍 **Real Duplicate Detection** – Compares SHA‑256 hashes of file contents, so even files with different names are correctly identified as duplicates.
- 📁 **Folder or Full System Scan** – Choose a specific folder for a quick cleanup, or scan all fixed drives (C:\, D:\, etc.) for a deep system‑wide check.
- 📭 **Zero‑Byte File Remover** – Detects every empty file (0 bytes) and deletes **all** of them – no copies kept.
- 🗑️ **Smart Deletion** – For non‑empty duplicates, keeps **one copy** per group and deletes the rest, so you never lose your only version.
- 📊 **Real‑Time Progress** – Live progress bar and status updates show exactly how many files have been scanned.
- ❌ **Cancel Anytime** – Stop the scan mid‑process without closing the application.
- 🎨 **Clean, Modern GUI** – Built with Python’s Tkinter (`ttk`), no external dependencies, and a clutter‑free interface.
- 🚀 **Standalone Executable** – Package the app as a single .exe file – no Python installation required on the target machine.

---

## 📸 Screenshots

*(Add your own screenshots here – e.g., main window, scan results)*

---

## 📦 Requirements

- Windows 10 / 11, Linux, or macOS (tested on all major OSes)
- Python 3.6 or higher (if running from source)
- No external libraries – uses only Python’s standard library (`os`, `hashlib`, `tkinter`, `threading`, etc.)

---

## 🔧 Installation & Running

### Option 1 – Run from source

1. Clone the repository
   ```bash
   git clone https://github.com/yourusername/duplicate-cleaner.git
   cd duplicate-cleaner
   ```

2. (Optional) Create a virtual environment
   ```bash
   python -m venv venv
   source venv/bin/activate      # On Linux/macOS
   venv\Scripts\activate         # On Windows
   ```

3. Launch the app
   ```bash
   python duplicate_cleaner.py
   ```

### Option 2 – Use the pre‑built executable

Download the latest `DuplicateCleaner.exe` from the Releases section, double‑click, and you're ready to go.

---

## 🚀 How to Use

1. Launch the application – you'll see a simple window with two main buttons.
2. **Scan a folder** – click **"Scan Folder"** and select any directory.
3. **Scan entire system** – click **"Scan Entire System"** to scan all fixed drives (confirmation required).
4. Watch the progress bar and status updates – the app counts files, calculates hashes, and groups duplicates in real time.
5. Review the results – the text area shows each duplicate group, including empty files (marked with a warning icon).
6. **Delete duplicates** – click **"Delete Duplicates"** to remove all found files:
   - All empty files are deleted completely.
   - For non‑empty groups, one copy is kept and the rest are deleted.
7. Confirm the action – a dialog shows exactly how many files will be removed.

**Pro tip:** The app can be cancelled anytime using the **Cancel** button – no data is lost, and you can restart later.

---

## 🧪 Building a Standalone .exe

If you want to share the app or use it without Python, package it with PyInstaller:

```bash
pip install pyinstaller
pyinstaller --onefile --windowed --name="DuplicateCleaner" duplicate_cleaner.py
```

The executable will be created in the `dist/` folder. You can rename it and move it anywhere.

---

## 📂 File Structure

```
duplicate-cleaner/
├── duplicate_cleaner.py      # Main application
├── README.md                 # This documentation
├── LICENSE                   # MIT License
├── .gitignore                # Git ignore rules
└── (no data files – all scanning is performed on‑the‑fly)
```

---

## ⚙️ Customisation

- **Change the hash algorithm** – replace `hashlib.sha256()` with `hashlib.md5()` or `blake2b` in `compute_hash()`.
- **Adjust chunk size** – modify `chunk_size` (default 8192 bytes) to balance speed vs. memory usage.
- **Add extension filters** – insert a check inside `scan_thread()` to skip certain file types (e.g., only scan `.jpg`, `.mp4`).
- **Change the "keep one" logic** – by default, the first file found (by path order) is kept; you can modify the deletion loop to keep the newest or oldest file instead.

---

## ❓ Troubleshooting

| Issue | Solution |
|-------|----------|
| "No module named 'tkinter'" | On Linux, install it with `sudo apt-get install python3-tk` (Debian/Ubuntu) or equivalent. |
| Scan is very slow | Try scanning a smaller folder first, or reduce the number of files. The hash calculation is CPU‑intensive. |
| Permission errors on some files | The app skips files it cannot read (e.g., system‑protected files). This is normal. |
| Deletion does nothing | Make sure you have write permissions in the target folders. Run as administrator if needed. |
| GUI looks different on your OS | Tkinter theme may vary; install `ttkthemes` for additional styling (not required). |

---

## 🤝 Contributing

Contributions, bug reports, and feature requests are always welcome!  
Here's how you can help:

1. Fork the repository.
2. Create a new branch (`git checkout -b feature/your-feature`).
3. Commit your changes (`git commit -m 'Add some feature'`).
4. Push to the branch (`git push origin feature/your-feature`).
5. Open a Pull Request – describe your changes clearly.

Please follow the existing code style and include tests where applicable.

---

## 💖 Support the Project

If you find Duplicate Cleaner useful and want to support its continued development, consider:

- **Starring** the repository on GitHub – it helps others discover the project.
- Reporting bugs or suggesting features via Issues.
- Buying me a coffee – every little bit keeps me motivated!

Thank you for using and supporting Duplicate Cleaner! 🙏

---

## 📄 License

This project is licensed under the MIT License.  
You are free to use, modify, and distribute it – see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgements

- Python's standard library – for providing all necessary tools with zero external dependencies.
- Hashlib – for reliable and fast hashing.
- Tkinter – for enabling a simple, cross‑platform GUI.
- All contributors and users who have provided feedback and inspiration.

---

Made with ❤️ for everyone who wants to reclaim their disk space and keep their files organized.

Happy cleaning! 🧹

---

⭐ If you like this project, please give it a star on GitHub! It really helps and motivates me to keep improving it.
