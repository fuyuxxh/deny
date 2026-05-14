"""NoLearn エントリーポイント"""

from src.gui import LoginGUI
from src.main import open_browser
import src.config as config
from tkinter import messagebox
from winrt.windows.media.ocr import OcrEngine
from winrt.windows.globalization import Language


def check_ocr_language():
    """en-USのOCRエンジンがインストールされているか確認する"""
    try:
        target_lang = "en-US"
        if not OcrEngine.is_language_supported(Language(target_lang)):
            print(f"  [Warning] {target_lang} のOCRエンジンが見つかりません。")
            messagebox.showwarning(
                "OCRエンジン未検出",
                f"WindowsのOCRエンジン（{target_lang}）が見つかりません。\n\n"
                "Windowsの設定から「時刻と言語」→「言語と地域」を開き、\n"
                "「英語 (米国)」の言語パックをインストールしてください。\n\n"
                "※これがないとReadingの自動解答が正しく動作しません。"
            )
        else:
            print(f"  [System] {target_lang} のOCRエンジンを確認しました。")
    except Exception as e:
        print(f"  [Error] OCRエンジンのチェック中にエラーが発生しました: {e}")


def main():
    # ---------------------------------------------------------
    # [設定] ここでプロジェクト全体のバッファ（待機時間）を変更できます
    config.DELAY_MIN = 2.0
    config.DELAY_MAX = 5.0
    # ---------------------------------------------------------
    # 0. OCRエンジンのチェック
    check_ocr_language()

    # 1. GUI を表示して入力を受け取る
    app = LoginGUI()
    result = app.run()

    # 2. GUI が正常に完了した場合のみブラウザを起動
    if result is not None:
        url, user_id, password = result
        open_browser(url, user_id, password)


if __name__ == "__main__":
    main()