import os
import time
import tkinter as tk
from tkinter import filedialog, messagebox

# --- настройки ---
BIG_FILE_SIZE = 100 * 1024 * 1024  # 100 МБ
ARCHIVE_EXT = {'.zip', '.rar', '.7z', '.tar', '.gz'}

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_FILE = os.path.join(BASE_DIR, "file_helper.log")

files_data = []


# --- логирование ---
def log(text):
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} | {text}\n")
    except:
        pass


# --- форматирование ---
def format_size(size):
    return f"{size / (1024 * 1024):.2f} МБ"


# --- сканирование директории ---
def scan_directory(path):
    files_data.clear()

    for root, _, files in os.walk(path):
        for name in files:
            full_path = os.path.join(root, name)
            ext = os.path.splitext(name)[1].lower()

            size = 0
            ctime = "неизвестно"
            available = True

            try:
                size = os.path.getsize(full_path)
            except Exception as e:
                available = False
                log(f"Недоступен размер: {full_path}")

            try:
                ctime = time.strftime(
                    "%Y-%m-%d %H:%M:%S",
                    time.localtime(os.path.getctime(full_path))
                )
            except Exception:
                available = False

            files_data.append({
                "path": full_path,
                "name": name,
                "size": size,
                "ctime": ctime,
                "available": available,
                "big": size > BIG_FILE_SIZE,
                "archive": ext in ARCHIVE_EXT
            })

    files_data.sort(key=lambda x: x["size"], reverse=True)
    log(f"Просканирована директория: {path}")


# --- GUI-обновление ---
def update_list():
    listbox.delete(0, tk.END)
    for f in files_data:
        status = "OK" if f["available"] else "НЕДОСТУПЕН"
        listbox.insert(
            tk.END,
            f"{f['name']} | {format_size(f['size'])} | {f['ctime']} | {status}"
        )


def choose_folder():
    path = filedialog.askdirectory()
    if not path:
        return

    scan_directory(path)
    update_list()
    show_special_files()


# --- большие архивы ---
def show_special_files():
    both = [f for f in files_data if f["big"] and f["archive"] and f["available"]]
    if not both:
        return

    msg = "Большие архивы:\n\n"
    for f in both:
        msg += f"{f['name']} ({format_size(f['size'])})\n"

    if messagebox.askyesno(
        "Найдены большие архивы",
        msg + "\n\nУдалить их НАВСЕГДА?"
    ):
        for f in both[:]:
            delete_file(f)
        update_list()


# --- удаление ---
def delete_selected():
    selection = listbox.curselection()
    if not selection:
        return

    file = files_data[selection[0]]

    if not file["available"]:
        messagebox.showwarning(
            "Недоступен",
            "Файл недоступен для удаления (OneDrive или нет прав)."
        )
        return

    if messagebox.askyesno(
        "Подтверждение",
        f"Удалить файл НАВСЕГДА?\n\n{file['name']}"
    ):
        delete_file(file)
        update_list()


def delete_file(file):
    try:
        os.remove(file["path"])
        log(f"Удалён: {file['path']}")
        files_data.remove(file)
    except Exception:
        messagebox.showerror(
            "Ошибка",
            "Не удалось удалить файл.\nВозможно, он используется другой программой."
        )


# --- GUI ---
root = tk.Tk()
root.title("Файловый помощник")
root.geometry("900x500")

frame = tk.Frame(root)
frame.pack(pady=10)

btn_choose = tk.Button(frame, text="Выбрать папку", command=choose_folder)
btn_choose.pack(side=tk.LEFT, padx=5)

btn_delete = tk.Button(
    frame,
    text="Удалить выбранный файл",
    command=delete_selected
)
btn_delete.pack(side=tk.LEFT, padx=5)

scrollbar = tk.Scrollbar(root)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

listbox = tk.Listbox(
    root,
    width=150,
    height=25,
    yscrollcommand=scrollbar.set
)
listbox.pack(padx=10, pady=10)

scrollbar.config(command=listbox.yview)

root.mainloop()