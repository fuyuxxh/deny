"""
ログイン情報入力GUI
- URL, ID, Password の入力フィールドを提供
- ID, Password は config.env に JSON形式で永続保存
- 保存成功時は on_success コールバックを呼び出す
"""

import tkinter as tk
from tkinter import messagebox
import json
import os


CONFIG_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config.env")


def load_config():
    """config.env から保存済みの設定を読み込む"""
    if not os.path.exists(CONFIG_PATH):
        return {}
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            content = f.read().strip()
            if not content:
                return {}
            return json.loads(content)
    except (json.JSONDecodeError, IOError):
        return {}


def save_config(user_id: str, password: str) -> bool:
    """ID と Password を config.env に JSON形式で保存する。成功時 True を返す。"""
    try:
        data = {"id": user_id, "password": password}
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except (IOError, OSError) as e:
        messagebox.showerror("保存エラー", f"config.env への保存に失敗しました:\n{e}")
        return False


class LoginGUI:
    """URL / ID / Password 入力用 GUI

    run() を呼ぶと GUI が表示され、実行ボタン押下後に
    (url, user_id, password) のタプルを返す。
    ウィンドウが×ボタンで閉じられた場合は None を返す。
    """

    # --- カラーパレット ---
    BG           = "#1e1e2e"
    BG_FIELD     = "#313244"
    FG           = "#cdd6f4"
    FG_DIM       = "#a6adc8"
    ACCENT       = "#89b4fa"
    ACCENT_HOVER = "#74c7ec"
    BORDER       = "#45475a"
    BTN_FG       = "#1e1e2e"

    FONT_FAMILY  = "Segoe UI"

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("NoLearn - ログイン設定")
        self.root.configure(bg=self.BG)
        self.root.resizable(False, False)

        # ウィンドウサイズ & 中央配置
        w, h = 460, 420
        sx = (self.root.winfo_screenwidth() - w) // 2
        sy = (self.root.winfo_screenheight() - h) // 2
        self.root.geometry(f"{w}x{h}+{sx}+{sy}")

        self._build_ui()
        self._load_saved_values()

    # ------------------------------------------------------------------ UI
    def _build_ui(self):
        # --- タイトル ---
        title = tk.Label(
            self.root, text="NoLearn", font=(self.FONT_FAMILY, 22, "bold"),
            bg=self.BG, fg=self.ACCENT,
        )
        title.pack(pady=(24, 2))

        subtitle = tk.Label(
            self.root, text="接続情報を入力してください",
            font=(self.FONT_FAMILY, 10), bg=self.BG, fg=self.FG_DIM,
        )
        subtitle.pack(pady=(0, 18))

        # --- 入力フィールド ---
        self.url_entry  = self._add_field("URL")
        self.id_entry   = self._add_field("ID")
        self.pass_entry = self._add_field("Password", show="●")

        # --- 実行ボタン ---
        btn_frame = tk.Frame(self.root, bg=self.BG)
        btn_frame.pack(pady=(22, 40))

        self.run_btn = tk.Label(
            btn_frame, text="実  行", font=(self.FONT_FAMILY, 12, "bold"),
            bg=self.ACCENT, fg=self.BTN_FG,
            padx=40, pady=8, cursor="hand2",
        )
        self.run_btn.pack()
        self.run_btn.bind("<Button-1>", lambda e: self._on_execute())
        self.run_btn.bind("<Enter>", lambda e: self.run_btn.config(bg=self.ACCENT_HOVER))
        self.run_btn.bind("<Leave>", lambda e: self.run_btn.config(bg=self.ACCENT))

    def _add_field(self, label_text: str, show: str = "") -> tk.Entry:
        """ラベル + エントリーの組を追加して Entry を返す"""
        frame = tk.Frame(self.root, bg=self.BG)
        frame.pack(fill="x", padx=48, pady=(0, 10))

        lbl = tk.Label(
            frame, text=label_text, font=(self.FONT_FAMILY, 10),
            bg=self.BG, fg=self.FG_DIM, anchor="w",
        )
        lbl.pack(fill="x")

        entry = tk.Entry(
            frame, font=(self.FONT_FAMILY, 12),
            bg=self.BG_FIELD, fg=self.FG,
            insertbackground=self.FG,
            relief="flat", bd=0,
            highlightthickness=1,
            highlightbackground=self.BORDER,
            highlightcolor=self.ACCENT,
        )
        if show:
            entry.config(show=show)
        entry.pack(fill="x", ipady=6)

        return entry

    # ----------------------------------------------------------- ロジック
    def _load_saved_values(self):
        """保存済みの ID / Password を復元する"""
        config = load_config()
        if "id" in config:
            self.id_entry.insert(0, config["id"])
        if "password" in config:
            self.pass_entry.insert(0, config["password"])

    def _on_execute(self):
        """実行ボタン押下時の処理"""
        url      = self.url_entry.get().strip()
        user_id  = self.id_entry.get().strip()
        password = self.pass_entry.get().strip()

        # バリデーション
        if not url:
            messagebox.showwarning("入力エラー", "URL を入力してください。")
            return
        if not user_id:
            messagebox.showwarning("入力エラー", "ID を入力してください。")
            return
        if not password:
            messagebox.showwarning("入力エラー", "Password を入力してください。")
            return

        # URL にプロトコルが無ければ https:// を付与
        if not url.startswith(("http://", "https://")):
            url = "https://" + url

        # 保存 — 成功時は結果を保持して GUI を閉じる
        if save_config(user_id, password):
            self.result = (url, user_id, password)
            self.root.destroy()

    # ---------------------------------------------------------------- 起動
    def run(self):
        """GUIを表示し、実行ボタンが押されたら (url, user_id, password) を返す。
        ウィンドウが閉じられた場合は None を返す。
        """
        self.result = None
        self.root.mainloop()
        return self.result
