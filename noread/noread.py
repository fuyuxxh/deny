# exe.py
import os
import sys
from tkinter import messagebox
import tkinter as tk

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

from src.gui import XreadApp
from src.main import login, autoread, quit

if getattr(sys, 'frozen', False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(__file__)

LOCK_FILE = os.path.join(BASE_DIR, "xread.lock")


def _is_process_alive(pid: int) -> bool:
    """指定PIDのプロセスが生存しているか確認する"""
    try:
        os.kill(pid, 0)
        return True
    except (OSError, ProcessLookupError):
        return False


def _acquire_lock() -> bool:
    """ロックファイルを取得する。既に実行中なら False を返す"""
    if os.path.exists(LOCK_FILE):
        try:
            with open(LOCK_FILE, "r") as f:
                old_pid = int(f.read().strip())
            # 前回のプロセスがまだ生きていれば多重起動
            if _is_process_alive(old_pid):
                return False
        except (ValueError, OSError):
            pass
        # 前回のプロセスは終了済み → ロック解放
        os.remove(LOCK_FILE)

    with open(LOCK_FILE, "w") as f:
        f.write(str(os.getpid()))
    return True


def _release_lock():
    """ロックファイルを解放する"""
    try:
        os.remove(LOCK_FILE)
    except OSError:
        pass


def main():
    if not _acquire_lock():
        root = tk.Tk()
        root.withdraw()
        messagebox.showwarning("実行中", "既に実行中です。")
        root.destroy()
        sys.exit(1)

    try:
        app = XreadApp()
        config = app.run()
        if not config:
            return
        options = Options()
        options.add_argument("--log-level=3")
        options.add_experimental_option("detach", True)
        driver = webdriver.Chrome(options=options)
        driver.set_window_size(768, 1024)
        driver.implicitly_wait(10)
        driver.get("https://www.xreading.com/login/index.php")
        login(driver, config["user_id"], config["password"])

        url_list = config.get("urls", [])
        print("Parsed URL list:", url_list)

        try:
            for url in url_list:
                autoread(driver, url)
            print("All readings are successfully completed.")
        except Exception as e:
            print(f"Error occurred while reading: {e}")
        quit(driver)
        
    except Exception as e:
        print(f"予期しないエラー: {e}")
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror("エラー", f"予期しないエラーが発生しました。\n\n{e}")
        root.destroy()
    finally:
        _release_lock()


if __name__ == "__main__":
    main()