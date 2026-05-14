import tkinter as tk
from tkinter import messagebox
import os
import sys
import re
import json

if getattr(sys, 'frozen', False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.dirname(__file__))


# URLバリデーション用パターン
URL_PATTERN = re.compile(
    r"^https://www\.xreading\.com/local/reader/index\.php\?cid=\d+&assignment=\d+$"
)


class XreadApp:
    """URL, ID, Passwordを入力するGUI画面"""

    # ── カラーパレット ──
    BG           = "#1a1a2e"
    BG_CARD      = "#16213e"
    ACCENT       = "#0f3460"
    HIGHLIGHT     = "#e94560"
    TEXT_PRIMARY  = "#eaeaea"
    TEXT_SECONDARY = "#a8a8b3"
    ENTRY_BG     = "#0f3460"
    ENTRY_FG     = "#ffffff"
    ENTRY_BORDER = "#e94560"
    BTN_BG       = "#e94560"
    BTN_FG       = "#ffffff"
    BTN_HOVER    = "#c73650"
    BTN_ADD_BG   = "#0f3460"
    BTN_DEL_BG   = "#8b0000"
    BTN_DEL_HOVER = "#a52a2a"

    FONT_TITLE = ("Segoe UI", 18, "bold")
    FONT_LABEL = ("Segoe UI", 11)
    FONT_ENTRY = ("Consolas", 11)
    FONT_BTN   = ("Segoe UI", 12, "bold")
    FONT_SMALL_BTN = ("Segoe UI", 10, "bold")

    CONFIG_PATH = os.path.join(BASE_DIR, "config.env")

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Xread - 設定")
        self.root.configure(bg=self.BG)
        self.root.resizable(False, False)

        self.config = None
        self.url_rows: list[dict] = []  # [{frame, entry, del_btn}, ...]
        self.entries: dict[str, tk.Entry] = {}

        self._build_ui()
        self._load_config()

    # ────────────────────────────────────────
    # UI 構築
    # ────────────────────────────────────────
    def _build_ui(self):
        # ── タイトル ──
        title = tk.Label(
            self.root, text="no-xreading", font=self.FONT_TITLE,
            bg=self.BG, fg=self.HIGHLIGHT, pady=18,
        )
        title.pack(fill="x")

        # ── スクロール可能なメインエリア ──
        self.canvas = tk.Canvas(self.root, bg=self.BG, highlightthickness=0)
        self.scrollbar = tk.Scrollbar(self.root, orient="vertical", command=self.canvas.yview)
        self.scroll_frame = tk.Frame(self.canvas, bg=self.BG)

        self.scroll_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        self.canvas_window = self.canvas.create_window((0, 0), window=self.scroll_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True, padx=(28, 0))
        self.scrollbar.pack(side="right", fill="y", padx=(0, 10))

        # Canvas幅をスクロールフレームに追従させる
        self.canvas.bind("<Configure>", self._on_canvas_configure)

        # マウスホイールでスクロール
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

        # ── URLセクション ──
        url_header = tk.Frame(self.scroll_frame, bg=self.BG_CARD)
        url_header.pack(fill="x", pady=(0, 0))

        tk.Label(
            url_header, text="URL（複数入力可）", font=self.FONT_LABEL,
            bg=self.BG_CARD, fg=self.TEXT_SECONDARY, anchor="w",
        ).pack(side="left", fill="x", expand=True, padx=(10, 0), pady=(10, 2))

        add_btn = tk.Button(
            url_header, text="＋ 追加", font=self.FONT_SMALL_BTN,
            bg=self.BTN_ADD_BG, fg=self.BTN_FG,
            activebackground=self.ACCENT, activeforeground=self.BTN_FG,
            relief="flat", cursor="hand2",
            padx=10, pady=2,
            command=self._add_url_row,
        )
        add_btn.pack(side="right", padx=(0, 10), pady=(10, 2))
        add_btn.bind("<Enter>", lambda e: add_btn.config(bg=self.ACCENT))
        add_btn.bind("<Leave>", lambda e: add_btn.config(bg=self.BTN_ADD_BG))

        # URLリストのコンテナ
        self.url_container = tk.Frame(self.scroll_frame, bg=self.BG_CARD)
        self.url_container.pack(fill="x", pady=(0, 8))

        # 初期URL行を1つ追加
        self._add_url_row()

        # ── 認証フィールド用カード ──
        card = tk.Frame(self.scroll_frame, bg=self.BG_CARD, padx=30, pady=12)
        card.pack(fill="x", pady=(0, 10))

        fields = [
            ("ユーザーID",  "user_id",  False),
            ("パスワード",  "password", True),
        ]

        for label_text, key, is_secret in fields:
            self._add_field(card, label_text, key, is_secret)

        # ── 実行ボタン ──
        btn_frame = tk.Frame(self.scroll_frame, bg=self.BG)
        btn_frame.pack(pady=(8, 20))

        self.run_btn = tk.Button(
            btn_frame, text="▶  実行", font=self.FONT_BTN,
            bg=self.BTN_BG, fg=self.BTN_FG,
            activebackground=self.BTN_HOVER, activeforeground=self.BTN_FG,
            relief="flat", cursor="hand2",
            padx=20, pady=8,
            command=self._on_run,
        )
        self.run_btn.pack()
        self.run_btn.bind("<Enter>", lambda e: self.run_btn.config(bg=self.BTN_HOVER))
        self.run_btn.bind("<Leave>", lambda e: self.run_btn.config(bg=self.BTN_BG))

        # ── 初期ウィンドウサイズ ──
        self.root.update_idletasks()
        w, h = 560, 600
        sx = (self.root.winfo_screenwidth()  - w) // 2
        sy = (self.root.winfo_screenheight() - h) // 2
        self.root.geometry(f"{w}x{h}+{sx}+{sy}")

    def _on_canvas_configure(self, event):
        self.canvas.itemconfig(self.canvas_window, width=event.width)

    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    # ────────────────────────────────────────
    # URL行の追加・削除
    # ────────────────────────────────────────
    def _add_url_row(self):
        """URL入力行を1つ追加する"""
        row_frame = tk.Frame(self.url_container, bg=self.BG_CARD)
        row_frame.pack(fill="x", padx=10, pady=(4, 0))

        entry = tk.Entry(
            row_frame, font=self.FONT_ENTRY,
            bg=self.ENTRY_BG, fg=self.ENTRY_FG,
            insertbackground=self.ENTRY_FG,
            relief="flat", bd=0,
            highlightthickness=2,
            highlightcolor=self.ENTRY_BORDER,
            highlightbackground=self.ACCENT,
        )
        entry.pack(side="left", fill="x", expand=True, ipady=6)

        del_btn = tk.Button(
            row_frame, text="✕", font=self.FONT_SMALL_BTN,
            bg=self.BTN_DEL_BG, fg=self.BTN_FG,
            activebackground=self.BTN_DEL_HOVER, activeforeground=self.BTN_FG,
            relief="flat", cursor="hand2",
            padx=8, pady=2,
        )
        del_btn.pack(side="right", padx=(6, 0))

        row_data = {"frame": row_frame, "entry": entry, "del_btn": del_btn}
        self.url_rows.append(row_data)

        # 削除ボタンのコマンドを設定
        del_btn.config(command=lambda r=row_data: self._remove_url_row(r))
        del_btn.bind("<Enter>", lambda e, b=del_btn: b.config(bg=self.BTN_DEL_HOVER))
        del_btn.bind("<Leave>", lambda e, b=del_btn: b.config(bg=self.BTN_DEL_BG))

    def _remove_url_row(self, row_data: dict):
        """URL入力行を削除する（最低1行は残す）"""
        if len(self.url_rows) <= 1:
            messagebox.showinfo("情報", "URLは最低1つ必要です。", parent=self.root)
            return
        row_data["frame"].destroy()
        self.url_rows.remove(row_data)

    # ────────────────────────────────────────
    # 共通フィールド追加
    # ────────────────────────────────────────
    def _add_field(self, parent: tk.Frame, label_text: str, key: str, is_secret: bool):
        """ラベル + エントリを1組追加する"""
        lbl = tk.Label(
            parent, text=label_text, font=self.FONT_LABEL,
            bg=self.BG_CARD, fg=self.TEXT_SECONDARY, anchor="w",
        )
        lbl.pack(fill="x", pady=(10, 2))

        entry = tk.Entry(
            parent, font=self.FONT_ENTRY,
            bg=self.ENTRY_BG, fg=self.ENTRY_FG,
            insertbackground=self.ENTRY_FG,
            relief="flat", bd=0,
            highlightthickness=2,
            highlightcolor=self.ENTRY_BORDER,
            highlightbackground=self.ACCENT,
            show="●" if is_secret else "",
        )
        entry.pack(fill="x", ipady=6)

        self.entries[key] = entry

    # ────────────────────────────────────────
    # config.env 読み書き
    # ────────────────────────────────────────
    def _load_config(self):
        """既存の config.env があればフィールドに復元する（URLは復元しない）"""
        if not os.path.exists(self.CONFIG_PATH):
            return
        try:
            with open(self.CONFIG_PATH, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("urls="):
                        continue  # URLは復元しない
                    if "=" in line:
                        key, value = line.split("=", 1)
                        key = key.strip()
                        value = value.strip()
                        if key in self.entries:
                            self.entries[key].insert(0, value)
        except Exception:
            pass

    def _save_config(self, values: dict, urls: list[str]):
        """入力値を config.env に書き出す"""
        with open(self.CONFIG_PATH, "w", encoding="utf-8") as f:
            # URLをJSON配列として1行で保存
            f.write(f"urls={json.dumps(urls, ensure_ascii=False)}\n")
            # その他のフィールド
            for key, value in values.items():
                f.write(f"{key}={value}\n")

    # ────────────────────────────────────────
    # イベントハンドラ
    # ────────────────────────────────────────
    def _on_run(self):
        """実行ボタン押下時の処理"""
        # URL収集
        urls = [row["entry"].get().strip() for row in self.url_rows]
        urls = [u for u in urls if u]  # 空欄除去

        # その他フィールド収集
        values = {k: e.get().strip() for k, e in self.entries.items()}

        # 空欄チェック
        if not urls:
            messagebox.showwarning(
                "入力エラー", "URLを1つ以上入力してください。",
                parent=self.root,
            )
            return

        empty = [k for k, v in values.items() if not v]
        if empty:
            messagebox.showwarning(
                "入力エラー",
                f"以下の項目が未入力です:\n  {', '.join(empty)}",
                parent=self.root,
            )
            return

        # URL バリデーション
        invalid = [u for u in urls if not URL_PATTERN.match(u)]
        if invalid:
            messagebox.showwarning(
                "URL エラー",
                "以下のURLが不正です:\n\n" + "\n".join(invalid)
                + "\n\n正しい形式:\nhttps://www.xreading.com/local/reader/index.php?cid=数字&assignment=数字",
                parent=self.root,
            )
            return

        # config.env に保存
        self._save_config(values, urls)
        self.config = {**values, "urls": urls}

        messagebox.showinfo(
            "保存完了",
            f"設定を保存しました。\nURL数: {len(urls)}",
            parent=self.root,
        )

        # GUIを閉じて後続処理へ
        self.root.destroy()

    # ────────────────────────────────────────
    # 起動
    # ────────────────────────────────────────
    def run(self):
        self.root.mainloop()
        return self.config