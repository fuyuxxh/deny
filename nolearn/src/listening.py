from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import random

def start_listening_learning(driver, timeout: int = 10) -> bool:
    """
    Listeningの「学習する」ボタンをクリックする。
    href="/student/listan/stlist/..." で始まるリンクを前方一致で探す。
    """
    print("\n  [Listening] 学習開始シーケンスを実行します...")
    
    selector_start = 'a[href^="/student/listan/stlist/"].btn_listan'
    
    try:
        elem = WebDriverWait(driver, timeout).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, selector_start))
        )
        elem.click()
        print("  ✓ [Listening] 「学習する」ボタンをクリックしました")
        
        # 遷移中を待機
        try:
            WebDriverWait(driver, timeout).until(EC.staleness_of(elem))
            print("  ✓ [Listening] 画面遷移を完了しました")
        except Exception:
            pass
            
        return True
    except Exception:
        print("  ✗ [Listening] 「学習する」ボタンが見つからないか、クリック不可です。")
        return False

def click_listening_player(driver, timeout: int = 10) -> bool:
    """
    resultTable 内の再生リンク（href^="/as/lplayer/index.cfm?"）をクリックする。
    """
    print("\n  [Listening] プレイヤーリンクを検索中...")
    
    xpath = '//*[@id="resultTable"]/tbody/tr/td[6]/a'
    selector_fallback = 'a[href^="/as/lplayer/index.cfm?"]'
    
    try:
        # まず XPath で試す
        elem = WebDriverWait(driver, timeout).until(
            EC.element_to_be_clickable((By.XPATH, xpath))
        )
        elem.click()
        print("  ✓ [Listening] プレイヤーリンクをクリックしました")
        
        # 遷移中を待機
        try:
            WebDriverWait(driver, timeout).until(EC.staleness_of(elem))
            print("  ✓ [Listening] 画面遷移を完了しました")
        except Exception:
            pass
            
        return True
    except Exception:
        # XPath で見つからない場合、CSS セレクタでフォールバック
        try:
            elem = WebDriverWait(driver, 3).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, selector_fallback))
            )
            elem.click()
            print("  ✓ [Listening] プレイヤーリンクをクリックしました (フォールバック)")
            
            try:
                WebDriverWait(driver, timeout).until(EC.staleness_of(elem))
                print("  ✓ [Listening] 画面遷移を完了しました")
            except Exception:
                pass
                
            return True
        except Exception:
            print("  ✗ [Listening] プレイヤーリンクが見つかりませんでした。")
            return False

def type_listening_answer(driver, timeout: int = 10) -> bool:
    """
    listan_box テキストエリアに定型文を入力する。
    """
    print("\n  [Listening] テキストボックスに入力中...")
    
    answer_text = "I'm I my me mine you your yours we our us ours they them their theirs do did can could would will it this these those let's it's"
    
    try:
        textarea = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.ID, "listan_box"))
        )
        textarea.clear()
        textarea.send_keys(answer_text)
        print("  ✓ [Listening] テキストボックスに入力しました")
        return True
    except Exception:
        print("  ✗ [Listening] テキストボックスが見つかりませんでした。")
        return False

def click_judge_button(driver, timeout: int = 10) -> bool:
    """
    「判定」ボタンをクリックする。
    """
    print("\n  [Listening] 「判定」ボタンを検索中...")
    
    xpath = '//*[@id="root"]/div/div/div/div/div[2]/div[2]/div/div[3]/div/button'
    
    try:
        btn = WebDriverWait(driver, timeout).until(
            EC.element_to_be_clickable((By.XPATH, xpath))
        )
        btn.click()
        print("  ✓ [Listening] 「判定」ボタンをクリックしました")
        delay = random.uniform(1.5, 5.0)
        print(f"  [System] 元のURLに戻る前に {delay:.1f} 秒待機します...")
        time.sleep(delay)
        return True
    except Exception:
        print("  ✗ [Listening] 「判定」ボタンが見つかりませんでした。")
        return False

def run_listening_automation(driver, url: str):
    """
    Listening学習を自動化するエントリー関数。
    """
    print("\n========================================")
    print("  [System] Listeningの自動学習処理を開始します")
    print("========================================")
    
    started = start_listening_learning(driver, timeout=5)
    
    if started:
        # resultTable 内のプレイヤーリンクをクリック
        clicked = click_listening_player(driver, timeout=5)
        if clicked:
            # テキストボックスに入力
            typed = type_listening_answer(driver, timeout=5)
            if typed:
                # 「判定」ボタンをクリック
                click_judge_button(driver, timeout=5)
        else:
            print("  [Listening] プレイヤーリンクが見つかりませんでした。")
    else:
        print("  [Listening] 学習する対象が見つかりませんでした。")
        
    # 状態をリセットするために元のURLに戻る
    driver.get(url)
