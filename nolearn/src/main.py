"""
Selenium を使って Chrome で指定 URL を開き、
ログインフォームに ID / Password を自動入力するモジュール。
index.py から呼び出される。

使い方:
    python main.py <url>
"""

import sys
import time
import random
import os
import json
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from .vocabulary import run_vocabulary_automation
from .grammar import run_grammar_automation
from .reading import run_reading_automation
from .dialogue import run_dialogue_automation
from .dictation import run_dictation_automation
from .listening import run_listening_automation

# --- セレクタのフォールバック候補 ---
_FALLBACK_ID_SELECTORS = [
    'input[name="username"]',
    'input[name="userid"]',
    'input[name="user"]',
    'input[name="login"]',
    'input[name="email"]',
    'input[type="text"]',
    'input[type="email"]',
    'input#username',
    'input#userid',
    'input#email',
]

_FALLBACK_PASS_SELECTORS = [
    'input[name="password"]',
    'input[name="pass"]',
    'input[type="password"]',
    'input#password',
]

_FALLBACK_BTN_SELECTORS = [
    'button[type="submit"]',
    'input[type="submit"]',
    'button.login',
    'button#login',
    '#login-btn',
    'button',
]


def _find_element_with_fallback(driver, fallback_list: list[str], timeout: int = 10):
    """リスト内のセレクタで要素が表示されるまで待機して探す。"""
    end_time = time.time() + timeout
    while time.time() < end_time:
        for sel in fallback_list:
            try:
                elems = driver.find_elements(By.CSS_SELECTOR, sel)
                for elem in elems:
                    if elem.is_displayed():
                        print(f"  ✓ セレクタ '{sel}' で要素を検出")
                        return elem
            except Exception:
                continue
        time.sleep(0.5)
    return None


# Chrome のリモートデバッグポート（固定）
_CHROME_DEBUG_PORT = 9222


def _is_chrome_debug_alive() -> bool:
    """リモートデバッグポートが応答しているか素早くチェックする。"""
    import socket
    print(f"  [Session] Chrome デバッグポート (localhost:{_CHROME_DEBUG_PORT}) の生存確認中...")
    try:
        sock = socket.create_connection(("localhost", _CHROME_DEBUG_PORT), timeout=2)
        sock.close()
        print(f"  [Session] ✓ ポート {_CHROME_DEBUG_PORT} は応答しています。")
        return True
    except (ConnectionRefusedError, socket.timeout, OSError) as e:
        print(f"  [Session] ✗ ポート {_CHROME_DEBUG_PORT} に接続できません。")
        print(f"  [Session]   エラー種別: {type(e).__name__}: {e}")
        return False


def _attach_to_existing_chrome():
    """既に起動している Chrome のデバッグポートに新しい ChromeDriver で接続する。"""
    print(f"  [Session] 既存の Chrome (デバッグポート {_CHROME_DEBUG_PORT}) に接続中...")
    options = Options()
    options.add_experimental_option("debuggerAddress", f"localhost:{_CHROME_DEBUG_PORT}")

    try:
        driver = webdriver.Chrome(options=options)
    except Exception as e:
        print(f"  [Session] ✗ 既存 Chrome への接続に失敗しました")
        print(f"  [Session]   エラー種別: {type(e).__name__}")
        print(f"  [Session]   詳細: {e}")
        cause = e.__cause__ or e.__context__
        depth = 0
        while cause and depth < 5:
            print(f"  [Session]   原因[{depth}]: {type(cause).__name__}: {cause}")
            cause = cause.__cause__ or cause.__context__
            depth += 1
        return None

    # 接続テスト
    print("  [Session] ブラウザの生存確認中...")
    try:
        title = driver.title
        print(f"  [Session] ✓ 既存 Chrome に接続しました (タイトル: {title[:50]})")
    except Exception as e:
        print(f"  [Session] ✗ 既存ブラウザから応答がありません")
        print(f"  [Session]   エラー種別: {type(e).__name__}: {e}")
        return None

    return driver


def open_browser(url: str, user_id: str = "", password: str = ""):
    """Chrome を起動して指定 URL を開き、ID / Password を自動入力する。
    前回の Chrome が生きていればそれに再接続する。
    """
    import traceback

    driver = None
    reused = False
    
    # --- 既存の Chrome に再接続を試みる ---
    if _is_chrome_debug_alive():
        try:
            driver = _attach_to_existing_chrome()
            if driver is not None:
                print("========================================")
                print("  既存のブラウザに再接続しました")
                print(f"  {url} にアクセスします...")
                print("========================================")
                driver.get(url)
                reused = True
        except Exception as e:
            print(f"  [System] 既存ブラウザへの接続をスキップします")
            print(f"  [System]   エラー種別: {type(e).__name__}")
            print(f"  [System]   メッセージ: {e}")
            print(f"  [System]   トレースバック:")
            traceback.print_exc()
            driver = None
            reused = False
    else:
        print("  [Session] → 新規ブラウザを起動します。")
    
    # --- 接続できなかった場合は新規起動 ---
    if not reused:
        options = Options()
        # ウィンドウサイズを 1280x720 に固定
        options.add_argument("--window-size=1280,720")
        # リモートデバッグポートを有効化（次回の再接続用）
        options.add_argument(f"--remote-debugging-port={_CHROME_DEBUG_PORT}")
        # ブラウザが自動終了しないようにする
        options.add_experimental_option("detach", True)

        driver = webdriver.Chrome(options=options)
        driver.get(url)

        print("========================================")
        print("  config.env への保存が正常に完了しました")
        print(f"  Chrome で {url} を開きました")
        print(f"  (デバッグポート {_CHROME_DEBUG_PORT} で次回再接続可能)")
        print("========================================")

    # --- 自動ログイン (新規起動時のみ) ---
    if user_id and password and not reused:
        print("\n  ログインフォームへの自動入力を開始...")

        # ID 入力欄を検索
        id_elem = _find_element_with_fallback(driver, _FALLBACK_ID_SELECTORS)
        if id_elem:
            id_elem.clear()
            id_elem.send_keys(user_id)
            print(f"  ✓ ID を入力しました")
        else:
            print("  ✗ ID 入力欄が見つかりませんでした")

        # Password 入力欄を検索
        pass_elem = _find_element_with_fallback(driver, _FALLBACK_PASS_SELECTORS)
        if pass_elem:
            pass_elem.clear()
            pass_elem.send_keys(password)
            print(f"  ✓ Password を入力しました")
        else:
            print("  ✗ Password 入力欄が見つかりませんでした")

        # ログインボタンを検索してクリック
        btn_elem = _find_element_with_fallback(driver, _FALLBACK_BTN_SELECTORS)
        if btn_elem:
            btn_elem.click()
            print(f"  ✓ ログインボタンをクリックしました")

            # ログインに伴う画面遷移を待機
            try:
                WebDriverWait(driver, 10).until(EC.staleness_of(btn_elem))
                print("  ✓ ログイン完了（画面遷移）を確認しました")
            except Exception:
                pass

            # もう一度指定された URL に遷移する
            print(f"  ✓ 再度 {url} にアクセスします...")
            driver.get(url)
        else:
            print("  ✗ ログインボタンが見つかりませんでした")
            print("========================================")
            return driver

    # --- 学習シーケンスを実行 ---
    # Vocabulary 自動学習シーケンスを実行
    run_vocabulary_automation(driver, url)
    
    # Grammar 自動学習シーケンスを実行
    run_grammar_automation(driver, url)
    
    # Reading 自動学習シーケンスを実行
    run_reading_automation(driver, url)
    
    # Dialogue 自動学習シーケンスを実行
    run_dialogue_automation(driver, url)
    
    # Dictation 自動学習シーケンスを実行
    run_dictation_automation(driver, url)
    
    # Listening 自動学習シーケンスを実行
    run_listening_automation(driver, url)

    print("========================================")

    return driver


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("使い方: python main.py <url>")
        sys.exit(1)

    target_url = sys.argv[1]
    open_browser(target_url)

