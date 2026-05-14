from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import random

def start_dictation_learning(driver, timeout: int = 10) -> bool:
    """
    Dictationの「学習する」ボタンをクリックする。
    href="/student/dictation/stlist/..." で始まるリンクを前方一致で探す。
    """
    print("\n  [Dictation] 学習開始シーケンスを実行します...")
    
    selector_start = 'a[href^="/student/dictation/stlist/"].btn_dictan'
    
    try:
        elem = WebDriverWait(driver, timeout).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, selector_start))
        )
        elem.click()
        print("  ✓ [Dictation] 「学習する」ボタンをクリックしました")
        
        # 遷移中を待機
        try:
            WebDriverWait(driver, timeout).until(EC.staleness_of(elem))
            print("  ✓ [Dictation] 画面遷移を完了しました")
        except Exception:
            pass
            
        return True
    except Exception:
        print("  ✗ [Dictation] 「学習する」ボタンが見つからないか、クリック不可です。")
        return False

def run_dictation_automation(driver, url: str):
    """
    Dictation学習を自動化するエントリー関数。
    現在は学習開始ボタンのクリックのみ実行する。
    """
    print("\n========================================")
    print("  [System] Dictationの自動学習処理を開始します")
    print("========================================")
    
    started = start_dictation_learning(driver, timeout=5)
    
    if started:
        print("  [Dictation] (※ここに後ほど問題を解くロジックを追加します)")
        time.sleep(2)
    else:
        print("  [Dictation] 学習する対象が見つかりませんでした。")
        
    # 状態をリセットするために元のURLに戻る
    driver.get(url)
