import os
import hashlib
import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext, messagebox
from threading import Thread, Event
import string
from collections import defaultdict

class DuplicateFinderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Duplicate File Finder – Full System")
        self.root.geometry("900x700")
        self.root.resizable(True, True)
        self.style = ttk.Style()
        self.style.theme_use("clam")

        # Control variables
        self.cancel_event = Event()
        self.is_scanning = False
        self.duplicates = {}   # hash -> list of paths
        self.total_scanned = 0
        self.total_groups = 0
        self.empty_file_hash = hashlib.sha256(b'').hexdigest()  # hash of empty files

        # --- Top frame: buttons ---
        top_frame = ttk.Frame(root, padding="10")
        top_frame.pack(fill=tk.X)

        ttk.Button(top_frame, text="📁 Scan Folder", command=self.scan_folder, width=15).pack(side=tk.LEFT, padx=5)
        ttk.Button(top_frame, text="💻 Scan Entire System", command=self.scan_system, width=20).pack(side=tk.LEFT, padx=5)
        self.btn_cancel = ttk.Button(top_frame, text="❌ Cancel", command=self.cancel_scan, state=tk.DISABLED)
        self.btn_cancel.pack(side=tk.LEFT, padx=5)

        self.lbl_folder = ttk.Label(top_frame, text="", foreground="gray")
        self.lbl_folder.pack(side=tk.LEFT, padx=10)

        # --- Progress bar ---
        self.progress = ttk.Progressbar(root, orient=tk.HORIZONTAL, length=100, mode='determinate')
        self.progress.pack(fill=tk.X, padx=10, pady=5)

        # Status label
        self.lbl_status = ttk.Label(root, text="Ready", foreground="blue")
        self.lbl_status.pack(pady=2)

        # --- Output area ---
        self.txt_output = scrolledtext.ScrolledText(root, wrap=tk.WORD, font=("Segoe UI", 10))
        self.txt_output.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # --- Bottom buttons for deletion ---
        bottom_frame = ttk.Frame(root, padding="5")
        bottom_frame.pack(fill=tk.X)

        self.btn_delete = ttk.Button(bottom_frame, text="🗑️ Delete Duplicates (Keep One, except empty files)", 
                                     command=self.delete_duplicates, state=tk.DISABLED)
        self.btn_delete.pack(side=tk.LEFT, padx=5)

        self.lbl_stats = ttk.Label(bottom_frame, text="")
        self.lbl_stats.pack(side=tk.LEFT, padx=10)

    # ------------------------------------------------------------
    #  Scan methods
    # ------------------------------------------------------------
    def scan_folder(self):
        folder = filedialog.askdirectory(title="Select Folder to Scan")
        if not folder:
            return
        self.start_scan(folder, system_scan=False)

    def scan_system(self):
        if not messagebox.askyesno("Confirm Full System Scan", 
                                    "This will scan ALL fixed drives (C:\, D:\, etc.).\nIt may take a long time.\nContinue?"):
            return
        drives = []
        if os.name == 'nt':  # Windows
            for letter in string.ascii_uppercase:
                drive = f"{letter}:\\"
                if os.path.exists(drive) and os.path.isdir(drive):
                    try:
                        import ctypes
                        drive_type = ctypes.windll.kernel32.GetDriveTypeW(drive)
                        if drive_type == 3:  # DRIVE_FIXED
                            drives.append(drive)
                    except:
                        drives.append(drive)
        else:  # Linux/Mac
            drives = ['/']
        if not drives:
            messagebox.showerror("Error", "No fixed drives found!")
            return
        self.start_scan(drives, system_scan=True)

    def start_scan(self, paths, system_scan=False):
        self.txt_output.delete(1.0, tk.END)
        self.progress['value'] = 0
        self.lbl_status.config(text="Preparing scan...", foreground="blue")
        self.btn_cancel.config(state=tk.NORMAL)
        self.btn_delete.config(state=tk.DISABLED)
        self.lbl_stats.config(text="")
        self.is_scanning = True
        self.cancel_event.clear()
        self.duplicates.clear()

        if isinstance(paths, str):
            paths = [paths]
        Thread(target=self.scan_thread, args=(paths, system_scan), daemon=True).start()

    def scan_thread(self, paths, system_scan):
        try:
            # First pass: count files
            total_files = 0
            self.root.after(0, lambda: self.lbl_status.config(text="Counting files..."))
            for root_path in paths:
                if self.cancel_event.is_set():
                    return
                for _, _, files in os.walk(root_path):
                    if self.cancel_event.is_set():
                        return
                    total_files += len(files)

            if total_files == 0:
                self.root.after(0, self.finish_scan, {})
                return

            self.root.after(0, lambda: self.progress.config(maximum=total_files))
            self.root.after(0, lambda: self.lbl_status.config(text=f"Scanning {total_files} files..."))

            hash_map = defaultdict(list)
            scanned = 0
            for root_path in paths:
                for dirpath, _, filenames in os.walk(root_path):
                    if self.cancel_event.is_set():
                        return
                    for fname in filenames:
                        if self.cancel_event.is_set():
                            return
                        file_path = os.path.join(dirpath, fname)
                        # Process ALL files (including empty)
                        try:
                            file_size = os.path.getsize(file_path)
                        except OSError:
                            scanned += 1
                            continue
                        # Compute hash (empty files get same hash)
                        file_hash = self.compute_hash(file_path)
                        if file_hash:
                            hash_map[file_hash].append(file_path)
                        scanned += 1
                        if scanned % 50 == 0:
                            self.root.after(0, lambda val=scanned: self.update_progress(val))
                            self.root.after(0, lambda val=scanned: self.lbl_status.config(
                                text=f"Scanning... {val}/{total_files} files"))

            # Filter groups with more than one file
            duplicates = {h: paths for h, paths in hash_map.items() if len(paths) > 1}
            self.root.after(0, self.finish_scan, duplicates)

        except Exception as e:
            self.root.after(0, self.show_error, str(e))
        finally:
            self.is_scanning = False
            self.root.after(0, lambda: self.btn_cancel.config(state=tk.DISABLED))

    def compute_hash(self, filepath, chunk_size=8192):
        hasher = hashlib.sha256()
        try:
            with open(filepath, "rb") as f:
                for chunk in iter(lambda: f.read(chunk_size), b""):
                    if self.cancel_event.is_set():
                        return None
                    hasher.update(chunk)
            return hasher.hexdigest()
        except (IOError, OSError, PermissionError):
            return None

    def update_progress(self, value):
        self.progress['value'] = value
        self.root.update_idletasks()

    def finish_scan(self, duplicates):
        self.duplicates = duplicates
        total_groups = len(duplicates)
        self.total_groups = total_groups
        self.progress['value'] = 0
        self.lbl_status.config(text="Scan complete", foreground="green")
        self.btn_delete.config(state=tk.NORMAL if total_groups > 0 else tk.DISABLED)

        # Build output
        output = ""
        if not duplicates:
            output = "✅ No duplicate files found.\n"
        else:
            total_dup_files = sum(len(paths) for paths in duplicates.values())
            total_size = 0
            empty_groups = 0
            for hash_val, paths in duplicates.items():
                for p in paths:
                    try:
                        size = os.path.getsize(p)
                        total_size += size
                    except:
                        pass
                if hash_val == self.empty_file_hash:
                    empty_groups += 1

            output = f"🔍 Found {total_groups} duplicate group(s), containing {total_dup_files} files.\n"
            output += f"💾 Total size of duplicates: {self.format_size(total_size)}\n"
            if empty_groups > 0:
                output += f"⚠️ Includes {empty_groups} group(s) of EMPTY files (0 bytes). These will be ALL deleted.\n"
            output += "\n"

            for idx, (hash_val, paths) in enumerate(duplicates.items(), 1):
                is_empty = (hash_val == self.empty_file_hash)
                label = "📁" if not is_empty else "📭"
                output += f"{label} Group #{idx} (SHA-256: {hash_val[:12]}...)\n"
                if is_empty:
                    output += f"   ⚠️  These files are EMPTY (0 bytes). ALL will be DELETED.\n"
                else:
                    output += f"   (One file will be kept, others deleted)\n"
                for p in paths:
                    output += f"   📄 {p}\n"
                output += "\n"
        self.txt_output.insert(tk.END, output)
        self.lbl_stats.config(text=f"Groups: {total_groups}")

    def show_error(self, err_msg):
        self.lbl_status.config(text="Error!", foreground="red")
        self.txt_output.insert(tk.END, f"❌ Error: {err_msg}\n")
        self.btn_cancel.config(state=tk.DISABLED)

    def cancel_scan(self):
        if self.is_scanning:
            self.cancel_event.set()
            self.lbl_status.config(text="Cancelling...", foreground="red")
            self.btn_cancel.config(state=tk.DISABLED)

    # ------------------------------------------------------------
    #  Delete duplicates (empty files: delete all; others: keep one)
    # ------------------------------------------------------------
    def delete_duplicates(self):
        if not self.duplicates:
            messagebox.showinfo("Info", "No duplicates to delete.")
            return

        # Separate empty and non-empty groups
        empty_groups = {h: paths for h, paths in self.duplicates.items() if h == self.empty_file_hash}
        non_empty_groups = {h: paths for h, paths in self.duplicates.items() if h != self.empty_file_hash}

        total_dup_files = sum(len(paths) for paths in self.duplicates.values())
        total_empty_files = sum(len(paths) for paths in empty_groups.values())
        total_nonempty_files = total_dup_files - total_empty_files

        msg = f"Are you sure you want to delete duplicate files?\n"
        msg += f"Total duplicate files: {total_dup_files}\n"
        if total_empty_files > 0:
            msg += f"⚠️  {total_empty_files} EMPTY file(s) will be ALL deleted (no copy kept).\n"
        if total_nonempty_files > 0:
            msg += f"For non‑empty files: {total_nonempty_files} file(s) will be deleted, keeping one per group.\n"
        msg += "\nThis action cannot be undone!"
        if not messagebox.askyesno("Confirm Deletion", msg):
            return

        deleted = 0
        errors = []

        # Delete all empty files
        for hash_val, paths in empty_groups.items():
            for path in paths:
                try:
                    os.remove(path)
                    deleted += 1
                except Exception as e:
                    errors.append(f"Could not delete {path}: {e}")

        # For non-empty groups: keep first, delete rest
        for hash_val, paths in non_empty_groups.items():
            keep = paths[0]
            for path in paths[1:]:
                try:
                    os.remove(path)
                    deleted += 1
                except Exception as e:
                    errors.append(f"Could not delete {path}: {e}")

        messagebox.showinfo("Deletion Complete", 
                            f"Deleted {deleted} duplicate file(s) in total.\n"
                            f"Errors: {len(errors)}")
        self.btn_delete.config(state=tk.DISABLED)
        self.lbl_stats.config(text=f"Deleted {deleted} files")
        self.txt_output.insert(tk.END, f"\n🗑️ Deleted {deleted} duplicate files (empty files all removed).\n")

    # ------------------------------------------------------------
    #  Helper
    # ------------------------------------------------------------
    def format_size(self, size_bytes):
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.2f} PB"

# ------------------------------------------------------------
if __name__ == "__main__":
    root = tk.Tk()
    app = DuplicateFinderApp(root)
    root.mainloop()