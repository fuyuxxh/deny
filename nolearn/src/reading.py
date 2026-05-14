from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import random

def start_reading_learning(driver, timeout: int = 10) -> bool:
    """
    Readingの「学習する」ボタンをクリックする。
    href="/student/selectedtraining/reading/stlist/..." で始まるリンクを前方一致で探す。
    """
    print("\n  [Reading] 学習開始シーケンスを実行します...")
    
    selector_start = 'a[href^="/student/selectedtraining/reading/stlist/"].btn_reading'
    
    try:
        elem = WebDriverWait(driver, timeout).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, selector_start))
        )
        elem.click()
        print("  ✓ [Reading] 「学習する」ボタンをクリックしました")
        
        # 遷移中を待機
        try:
            WebDriverWait(driver, timeout).until(EC.staleness_of(elem))
            print("  ✓ [Reading] 画面遷移を完了しました")
        except Exception:
            pass
            
        return True
    except Exception:
        print("  ✗ [Reading] 「学習する」ボタンが見つからないか、クリック不可です。")
        return False

def run_reading_automation(driver, url: str):
    """
    Reading学習を自動化するエントリー関数。
    現在は学習開始ボタンのクリックのみ実行する。
    """
    print("\n========================================")
    print("  [System] Readingの自動学習処理を開始します")
    print("========================================")
    
    started = start_reading_learning(driver, timeout=5)
    
    if started:
        print("  [Reading] (※ここに後ほど問題を解くロジックを追加します)")
        time.sleep(2)
    else:
        print("  [Reading] 学習する対象が見つかりませんでした。")
        
    # 状態をリセットするために元のURLに戻る
    driver.get(url)
