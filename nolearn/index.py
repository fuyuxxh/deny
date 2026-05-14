"""NoLearn エントリーポイント"""

from src.gui import LoginGUI
from src.main import open_browser
import src.config as config


def main():
    # ---------------------------------------------------------
    # [設定] ここでプロジェクト全体のバッファ（待機時間）を変更できます
    config.DELAY_MIN = 2.0
    config.DELAY_MAX = 5.0
    # ---------------------------------------------------------
    # 1. GUI を表示して入力を受け取る
    app = LoginGUI()
    result = app.run()

    # 2. GUI が正常に完了した場合のみブラウザを起動
    if result is not None:
        url, user_id, password = result
        open_browser(url, user_id, password)


if __name__ == "__main__":
    main()