import os
import time
import subprocess
from PIL import Image
import tkinter as tk
from tkinter import filedialog, ttk, messagebox

# Base directory of the app (where the .exe will live after packaging)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FFMPEG_PATH = os.path.join(BASE_DIR, "ffmpeg", "ffmpeg.exe")

cancel_flag = False
selected_files = []
output_folder = None
base_input_folder = None

# ---------- IMAGE COMPRESSION ----------
def compress_image(filepath, output_path, quality):
    if filepath.lower().endswith(".png"):
        output_path = output_path.replace(".png", ".jpg")

    print(f"[IMAGE] Compressing: {filepath} -> {output_path}")

    try:
        img = Image.open(filepath)
        if filepath.lower().endswith(".png"):
            img = img.convert("RGB")
        img.save(output_path, "JPEG", quality=quality, optimize=True)
        return "processed"
    except Exception as e:
        print(f"[IMAGE ERROR] {e}")
        return "error"

# ---------- VIDEO COMPRESSION ----------
def compress_video(filepath, output_path, crf):
    name, ext = os.path.splitext(output_path)
    output_path = f"{name}_compressed.mp4"

    print(f"[VIDEO] Compressing: {filepath} -> {output_path}")

    try:
        cmd = [
            FFMPEG_PATH,
            "-y",  # overwrite existing files
            "-i", filepath,
            "-vcodec", "libx264",
            "-crf", str(crf),
            output_path
        ]
        print(f"[FFMPEG CMD] {' '.join(cmd)}")
        subprocess.run(cmd, check=True)
        return "processed"
    except Exception as e:
        print(f"[VIDEO ERROR] {e}")
        return "error"

# ---------- UNIVERSAL HANDLER ----------
def compress_files(filepaths, image_quality, video_quality, output_folder, base_input_folder=None):
    global cancel_flag
    cancel_flag = False

    total = len(filepaths)
    processed, skipped = 0, 0
    start = time.time()

    progress_win = tk.Toplevel()
    progress_win.title("Compression Progress")
    label = tk.Label(progress_win, text="Starting compression...")
    label.pack(pady=10)
    bar = ttk.Progressbar(progress_win, length=300, mode="determinate")
    bar.pack(pady=10)

    def cancel_task():
        global cancel_flag
        cancel_flag = True

    cancel_btn = tk.Button(progress_win, text="Cancel", command=cancel_task)
    cancel_btn.pack(pady=5)

    for idx, filepath in enumerate(filepaths, start=1):
        if cancel_flag:
            label.config(text="❌ Cancelled. You can start again.")
            progress_win.update()
            break

        # Preserve original subfolder structure
        if base_input_folder:
            rel_path = os.path.relpath(filepath, base_input_folder)
            target_path = os.path.join(output_folder, rel_path)
            os.makedirs(os.path.dirname(target_path), exist_ok=True)
        else:
            target_path = os.path.join(output_folder, os.path.basename(filepath))

        ext = filepath.lower()
        if ext.endswith((".jpg",".jpeg",".png")):
            result = compress_image(filepath, target_path, image_quality)
        elif ext.endswith((".mp4",".avi",".mov",".mpg")):
            crf = int(32 - ((video_quality - 20) / 60) * 14)
            result = compress_video(filepath, target_path, crf)
        else:
            result = "skipped"

        if result == "processed":
            processed += 1
        elif result == "skipped":
            skipped += 1

        percent = (idx / total) * 100
        bar["value"] = percent
        label.config(text=f"{processed} done, {skipped} skipped ({percent:.2f}%)")
        progress_win.update()

    if not cancel_flag:
        elapsed = time.time() - start
        label.config(text=f"✅ Finished! {processed} compressed, {skipped} skipped in {elapsed:.1f}s")
        progress_win.update()
        time.sleep(3)
    progress_win.destroy()

# ---------- MAIN APP ----------
def start_app():
    global selected_files, output_folder, base_input_folder
    root = tk.Tk()
    root.title("Universal Image & Video Compressor")
    root.geometry("450x500")

    # Sliders
    tk.Label(root, text="Image Compression Capacity (20–80)").pack(pady=5)
    image_quality_var = tk.IntVar(value=40)
    tk.Scale(root, from_=20, to=80, orient="horizontal", variable=image_quality_var).pack(pady=5)

    tk.Label(root, text="Video Compression Capacity (20–80)").pack(pady=5)
    video_quality_var = tk.IntVar(value=40)
    tk.Scale(root, from_=20, to=80, orient="horizontal", variable=video_quality_var).pack(pady=5)

    # Input folder selection
    def select_input_folder():
        global selected_files, base_input_folder
        folder = filedialog.askdirectory(title="Select Input Folder")
        if folder:
            base_input_folder = folder
            selected_files = []
            for root_dir, _, files in os.walk(folder):
                for f in files:
                    if f.lower().endswith((".jpg",".jpeg",".png",".mp4",".avi",".mov",".mpg")):
                        selected_files.append(os.path.join(root_dir, f))
            print(f"[INFO] Selected {len(selected_files)} files from {folder}")

    def select_output_folder():
        global output_folder
        folder = filedialog.askdirectory(title="Select Output Folder")
        if folder:
            output_folder = folder
            print(f"[INFO] Output folder set to {output_folder}")

    def start_compression():
        if not selected_files:
            messagebox.showwarning("No files", "Please select an input folder first.")
            return
        if not output_folder:
            messagebox.showwarning("No output folder", "Please select an output folder.")
            return
        compress_files(selected_files, image_quality_var.get(), video_quality_var.get(), output_folder, base_input_folder)

    tk.Button(root, text="Select Input Folder", command=select_input_folder).pack(pady=10)
    tk.Button(root, text="Select Output Folder", command=select_output_folder).pack(pady=10)
    tk.Button(root, text="OK / Start Compression", command=start_compression).pack(pady=20)

    root.mainloop()

if __name__ == "__main__":
    start_app()
