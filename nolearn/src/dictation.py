from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import time
import random
import src.config as config

def navigate_to_dictation_list(driver, timeout: int = 10) -> bool:
    """
    メインページからDictationのリスト画面へ遷移する。
    Listeningと同様に、まず /student/dictation/stlist/ へのリンクをクリック。
    """
    print("\n  [Dictation] リスト画面への遷移を開始します...")
    
    selectors = [
        'a[href^="/student/dictation/stlist/"]',
        'a[href*="dictation"][href*="stlist"]',
    ]
    
    for sel in selectors:
        try:
            elem = WebDriverWait(driver, timeout).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, sel))
            )
            elem.click()
            print(f"  ✓ [Dictation] リスト画面へのリンクをクリックしました (セレクタ: {sel})")
            
            try:
                WebDriverWait(driver, timeout).until(EC.staleness_of(elem))
                print("  ✓ [Dictation] リスト画面への遷移を完了しました")
            except Exception:
                pass
                
            return True
        except Exception:
            continue
    
    print("  ✗ [Dictation] リスト画面へのリンクが見つかりませんでした。")
    return False

def click_dictation_player(driver, timeout: int = 10) -> bool:
    """
    リスト画面から「学習する」ボタン（btn_dictan）をクリックする。
    """
    print("\n  [Dictation] 「学習する」プレイヤーリンクを検索中...")
    
    selectors = [
        'a.btn_dictan',
        'a.btn_dictan.btn-block',
        'a[href^="/as/lplayer/index.cfm?"].btn_dictan',
    ]
    xpath_fallback = '//*[@id="resultTable"]/tbody/tr/td//a[contains(@class, "btn_dictan")]'
    
    for sel in selectors:
        try:
            elem = WebDriverWait(driver, timeout).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, sel))
            )
            elem.click()
            print(f"  ✓ [Dictation] 「学習する」をクリックしました (セレクタ: {sel})")
            
            try:
                WebDriverWait(driver, timeout).until(EC.staleness_of(elem))
                print("  ✓ [Dictation] プレイヤー画面への遷移を完了しました")
            except Exception:
                pass
                
            return True
        except Exception:
            continue
    
    try:
        elem = WebDriverWait(driver, 3).until(
            EC.element_to_be_clickable((By.XPATH, xpath_fallback))
        )
        elem.click()
        print("  ✓ [Dictation] 「学習する」をクリックしました (XPath フォールバック)")
        
        try:
            WebDriverWait(driver, timeout).until(EC.staleness_of(elem))
            print("  ✓ [Dictation] プレイヤー画面への遷移を完了しました")
        except Exception:
            pass
            
        return True
    except Exception:
        pass
    
    print("  ✗ [Dictation] 「学習する」プレイヤーリンクが見つかりませんでした。")
    return False

def click_start_button(driver, timeout: int = 10) -> bool:
    """
    Dictation学習画面の「スタート」ボタンをクリックする。
    """
    print("\n  [Dictation] 「スタート」ボタンを検索中...")
    
    xpath = '/html/body/div[2]/div/div[1]/div/div/div/div[2]/button'
    
    try:
        btn = WebDriverWait(driver, timeout).until(
            EC.element_to_be_clickable((By.XPATH, xpath))
        )
        btn.click()
        print("  ✓ [Dictation] 「スタート」ボタンをクリックしました")
        delay = random.uniform(config.DELAY_MIN, config.DELAY_MAX)
        print(f"  [System] スタート後の読み込みを待機中... ({delay:.1f} 秒)")
        time.sleep(delay)
        return True
    except Exception:
        print("  ✗ [Dictation] 「スタート」ボタンが見つかりませんでした。")
        return False

def click_fulltext_button(driver, timeout: int = 10) -> bool:
    """
    「全文」ボタンをクリックする。
    """
    print("\n  [Dictation] 「全文」ボタンを検索中...")
    
    xpath = '//*[@id="root"]/div/div/div/div/div/div[2]/div[2]/div/div[3]/div[2]/div[3]/div/button'
    
    try:
        btn = WebDriverWait(driver, timeout).until(
            EC.element_to_be_clickable((By.XPATH, xpath))
        )
        btn.click()
        print("  ✓ [Dictation] 「全文」ボタンをクリックしました")
        delay = random.uniform(config.DELAY_MIN, config.DELAY_MAX)
        print(f"  [System] 全文表示の読み込みを待機中... ({delay:.1f} 秒)")
        time.sleep(delay)
        return True
    except Exception:
        print("  ✗ [Dictation] 「全文」ボタンが見つかりませんでした。")
        return False

def click_retry_button(driver, timeout: int = 10) -> bool:
    """
    「もう一度」ボタンをクリックする。
    """
    print("\n  [Dictation] 「もう一度」ボタンを検索中...")
    
    xpath = '//*[@id="root"]/div/div/div/div/div/div[1]/div/div/div/div/div/div[2]/div/button'
    
    try:
        btn = WebDriverWait(driver, timeout).until(
            EC.element_to_be_clickable((By.XPATH, xpath))
        )
        btn.click()
        print("  ✓ [Dictation] 「もう一度」ボタンをクリックしました")
        delay = random.uniform(config.DELAY_MIN, config.DELAY_MAX)
        print(f"  [System] 再試行の読み込みを待機中... ({delay:.1f} 秒)")
        time.sleep(delay)
        return True
    except Exception:
        print("  ✗ [Dictation] 「もう一度」ボタンが見つかりませんでした。")
        return False

def extract_fulltext_from_dom(driver) -> str:
    """
    全文表示画面の DOM から文字を1文字ずつ抽出して結合する。
    構造: //*[@id="root"]/.../span[x]/div[y]/div に1文字ずつ格納されている。
    各 span 内の div を順に結合し、さらに span 間をスペースで結合する。
    """
    print("\n  [Dictation] DOM からテキストを抽出中...")
    
    base_xpath = '//*[@id="root"]/div/div/div/div/div/div[2]/div[2]/div/div[1]/div[2]/div/div'
    
    spans = driver.find_elements(By.XPATH, f'{base_xpath}/span')
    span_count = len(spans)
    
    if span_count == 0:
        print("  ✗ [Dictation] span 要素が見つかりませんでした。")
        return ""
    
    print(f"  [Dictation] span 要素数: {span_count}")
    
    all_span_texts = []
    
    for x in range(1, span_count + 1):
        divs = driver.find_elements(By.XPATH, f'{base_xpath}/span[{x}]/div')
        div_count = len(divs)
        
        span_chars = []
        for y in range(1, div_count + 1):
            try:
                elem = driver.find_element(By.XPATH, f'{base_xpath}/span[{x}]/div[{y}]/div')
                char = elem.text.strip()
                if char:
                    span_chars.append(char)
            except Exception:
                continue
        
        span_text = ''.join(span_chars)
        if span_text:
            all_span_texts.append(span_text)
            print(f"    span[{x}] ({div_count} 文字): {span_text}")
    
    full_text = ' '.join(all_span_texts)
    
    print(f"\n  ✓ [Dictation] 抽出テキスト:")
    print(f"      {full_text}")
    
    return full_text

def type_text_slowly(driver, text: str, delay_per_char: float = 0.25):
    """
    テキストを1文字ずつ、指定間隔でタイプする。
    """
    print(f"\n  [Dictation] テキストを入力中... ({len(text)} 文字, 1文字あたり {delay_per_char} 秒)")
    
    for i, char in enumerate(text):
        ActionChains(driver).send_keys(char).perform()
        time.sleep(delay_per_char)
        if (i + 1) % 10 == 0:
            print(f"    [{i+1}/{len(text)}] 入力中...")
    
    print(f"  ✓ [Dictation] テキスト入力完了 ({len(text)} 文字)")

def run_dictation_automation(driver, url: str):
    """
    Dictation学習を自動化するエントリー関数。
    フロー:
      1. メインページ → リスト画面へ遷移
      2. リスト画面 → 「学習する」プレイヤーリンクをクリック
      3. 「スタート」ボタンをクリック
      4. 「全文」ボタンをクリック → DOM からテキスト抽出
      5. 「もう一度」ボタンをクリック
      6. 「スタート」ボタンを再度クリック
      7. 抽出テキストを1文字0.25秒でタイプ
    """
    print("\n========================================")
    print("  [System] Dictationの自動学習処理を開始します")
    print("========================================")
    
    # ステップ1: リスト画面へ遷移
    navigated = navigate_to_dictation_list(driver, timeout=5)
    if not navigated:
        print("  [Dictation] リスト画面が見つかりませんでした。")
        driver.get(url)
        return

    # ステップ2: 「学習する」プレイヤーリンクをクリック
    clicked = click_dictation_player(driver, timeout=5)
    if not clicked:
        print("  [Dictation] プレイヤーリンクが見つかりませんでした。")
        driver.get(url)
        return

    # ステップ3: 「スタート」ボタンをクリック（1回目）
    started = click_start_button(driver, timeout=10)
    if not started:
        print("  [Dictation] スタートボタンが見つかりませんでした。")
        driver.get(url)
        return

    # ステップ4: 「全文」ボタンをクリック → DOM からテキスト抽出
    fulltext_clicked = click_fulltext_button(driver, timeout=10)
    if not fulltext_clicked:
        print("  [Dictation] 全文ボタンが見つかりませんでした。")
        driver.get(url)
        return

    extracted_text = extract_fulltext_from_dom(driver)
    if not extracted_text:
        print("  [Dictation] テキストの抽出に失敗しました。")
        driver.get(url)
        return

    # ステップ5: 「もう一度」ボタンをクリック
    retried = click_retry_button(driver, timeout=10)
    if not retried:
        print("  [Dictation] もう一度ボタンが見つかりませんでした。")
        driver.get(url)
        return

    # ステップ6: 「スタート」ボタンを再度クリック
    started2 = click_start_button(driver, timeout=10)
    if not started2:
        print("  [Dictation] 2回目のスタートボタンが見つかりませんでした。")
        driver.get(url)
        return

    # ステップ7: 抽出テキストを1文字0.05秒でタイプ
    type_text_slowly(driver, extracted_text, delay_per_char=0.05)

    # 状態をリセットするために元のURLに戻る
    delay = random.uniform(config.DELAY_MIN, config.DELAY_MAX)
    print(f"  [System] 元のURLに戻る前に {delay:.1f} 秒待機します...")
    time.sleep(delay)
    driver.get(url)
