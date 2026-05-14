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

from src.vocabulary import run_vocabulary_automation
from src.grammar import run_grammar_automation
from src.reading import run_reading_automation
from src.dialogue import run_dialogue_automation
from src.dictation import run_dictation_automation
from src.listening import run_listening_automation

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


_SESSION_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "session.json")

def _save_session(driver):
    """ドライバのセッション情報をファイルに保存する。"""
    session_data = {
        "executor_url": driver.service.service_url,
        "session_id": driver.session_id,
    }
    with open(_SESSION_FILE, "w") as f:
        json.dump(session_data, f)
    print(f"  [System] セッション情報を保存しました: {_SESSION_FILE}")

def _load_session():
    """保存済みのセッション情報からドライバに再接続する。"""
    if not os.path.exists(_SESSION_FILE):
        return None
    
    with open(_SESSION_FILE, "r") as f:
        session_data = json.load(f)
    
    executor_url = session_data["executor_url"]
    session_id = session_data["session_id"]
    
    # 既存のセッションに接続する
    from selenium.webdriver.remote.webdriver import WebDriver as RemoteWebDriver
    driver = RemoteWebDriver(command_executor=executor_url, options=Options())
    
    # 新しいセッションが作られてしまうので、古いセッションを閉じて差し替える
    driver.close()
    driver.session_id = session_id
    
    # 接続テスト（タイトル取得で生存確認）
    _ = driver.title
    return driver

def open_browser(url: str, user_id: str = "", password: str = ""):
    """Chrome を起動して指定 URL を開き、ID / Password を自動入力する。
    前回のセッションが生きていればそれに再接続する。
    """
    driver = None
    reused = False
    
    # --- 既存のセッションに再接続を試みる ---
    try:
        driver = _load_session()
        if driver is not None:
            print("========================================")
            print("  既存のブラウザセッションに再接続しました")
            print(f"  {url} にアクセスします...")
            print("========================================")
            driver.get(url)
            reused = True
    except Exception as e:
        print(f"  [System] 既存セッションへの接続をスキップします ({e})")
        driver = None
        reused = False
    
    # --- 接続できなかった場合は新規起動 ---
    if not reused:
        options = Options()
        # ウィンドウサイズを 1280x720 に固定
        options.add_argument("--window-size=1280,720")
        # ブラウザが自動終了しないようにする
        options.add_experimental_option("detach", True)

        driver = webdriver.Chrome(options=options)
        driver.get(url)
        
        # セッション情報を保存（次回から再接続可能にする）
        _save_session(driver)

        print("========================================")
        print("  config.env への保存が正常に完了しました")
        print(f"  Chrome で {url} を開きました")
        print("  (次回からは同じブラウザに再接続できます)")
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

