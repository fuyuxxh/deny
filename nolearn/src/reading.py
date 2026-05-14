from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import random
import os
import requests
import src.config as config

# --- メモリ上へのデータ保存用変数 ---
_reading_extracted_answers = {}

def click_reading_stlist(driver, timeout: int = 10) -> bool:
    """
    Readingの「stlist」ボタンをクリックする。
    """
    print("\n  [Reading] 「stlist」ボタンを検索中...")
    
    selector = 'a[href^="/student/selectedtraining/reading/stlist/"].btn_reading'
    
    try:
        elem = WebDriverWait(driver, timeout).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
        )
        elem.click()
        print("  ✓ [Reading] 「stlist」ボタンをクリックしました")
        
        try:
            WebDriverWait(driver, timeout).until(EC.staleness_of(elem))
            print("  ✓ [Reading] 画面遷移を完了しました")
        except Exception:
            pass
            
        return True
    except Exception:
        print("  ✗ [Reading] 「stlist」ボタンが見つからないか、クリック不可です。")
        return False

def click_reading_stunit(driver, timeout: int = 10) -> bool:
    """
    Readingの「stunit」ボタンをクリックする。
    """
    print("\n  [Reading] 「stunit」ボタンを検索中...")
    
    selector = 'a[href^="/student/selectedtraining/reading/stunit/"].btn_reading'
    
    try:
        elem = WebDriverWait(driver, timeout).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
        )
        elem.click()
        print("  ✓ [Reading] 「stunit」ボタンをクリックしました")
        
        try:
            WebDriverWait(driver, timeout).until(EC.staleness_of(elem))
            print("  ✓ [Reading] 画面遷移を完了しました")
        except Exception:
            pass
            
        return True
    except Exception:
        print("  ✗ [Reading] 「stunit」ボタンが見つからないか、クリック不可です。")
        return False

def click_reading_player(driver, timeout: int = 10) -> bool:
    """
    Readingのプレイヤーリンク（学習する）をクリックする。
    指定されたXPathを厳密に使用する。
    """
    print("\n  [Reading] 「学習する」プレイヤーリンクを検索中...")
    
    xpath = '//*[@id="main-container"]/div[2]/div/div[4]/div/div[4]/div/div/div[1]/div[3]/a'
    
    try:
        elem = WebDriverWait(driver, timeout).until(
            EC.element_to_be_clickable((By.XPATH, xpath))
        )
        elem.click()
        print("  ✓ [Reading] 「学習する」をクリックしました")
        
        try:
            WebDriverWait(driver, timeout).until(EC.staleness_of(elem))
            print("  ✓ [Reading] プレイヤー画面への遷移を完了しました")
        except Exception:
            pass
            
        return True
    except Exception:
        print("  ✗ [Reading] 「学習する」プレイヤーリンクが見つかりませんでした。")
        return False

def extract_reading_data(driver, timeout: int = 10) -> bool:
    """
    回答の文字列（x=2,3,4,5）と画像を抽出する。
    """
    global _reading_extracted_answers
    print("\n  [Reading] 画像と回答の文字列を抽出中...")
    
    # 1. 画像のダウンロード
    img_xpath = '//*[@id="root"]/div/div/div[2]/div/div/div[3]/div[3]/div/table[2]/tbody/tr[1]/td/div/div[2]/div[1]/img'
    try:
        img_elem = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.XPATH, img_xpath))
        )
        src = img_elem.get_attribute("src")
        if src:
            os.makedirs('./temp', exist_ok=True)
            
            # Seleniumのクッキーを使って画像をダウンロード
            cookies = driver.get_cookies()
            session = requests.Session()
            for cookie in cookies:
                session.cookies.set(cookie['name'], cookie['value'])
                
            response = session.get(src)
            if response.status_code == 200:
                filepath = './temp/reading_image.png'
                with open(filepath, 'wb') as f:
                    f.write(response.content)
                print(f"  ✓ [Reading] 画像をダウンロードしました: {filepath}")
            else:
                print(f"  ✗ [Reading] 画像のダウンロードに失敗しました。ステータスコード: {response.status_code}")
    except Exception as e:
        print(f"  ✗ [Reading] 画像の抽出に失敗しました: {e}")
        
    # 2. 回答の文字列の抽出
    _reading_extracted_answers.clear()
    base_xpath = '//*[@id="root"]/div/div/div[2]/div/div/div[3]/div[3]/div/table[2]/tbody/tr[{}]/td[3]/div[1]/div[4]/div[2]'
    
    # x = 2, 3, 4, 5
    for x in range(2, 6):
        ans_num = x - 1 # 1, 2, 3, 4 として保存
        xpath = base_xpath.format(x)
        try:
            ans_elem = WebDriverWait(driver, 2).until(
                EC.presence_of_element_located((By.XPATH, xpath))
            )
            text = ans_elem.text.strip()
            
            # プレフィックスを削除
            for prefix in ['a. ', 'b. ', 'c. ', 'd. ', 'e. ', 'A. ', 'B. ', 'C. ', 'D. ', 'E. ']:
                if text.startswith(prefix):
                    text = text[len(prefix):].strip()
                    break
                    
            _reading_extracted_answers[ans_num] = text
            print(f"  ✓ [Reading] 回答 {ans_num}: {text}")
        except Exception:
            # 見つからなくなったら終了
            break
            
    return True

def click_reading_confirm(driver, timeout: int = 10) -> bool:
    """
    「採点」ボタン（confirmButton）をクリックする。
    """
    print("\n  [Reading] 「採点」ボタンを検索中...")
    
    xpath = '//*[@id="confirmButton"]'
    
    try:
        btn = WebDriverWait(driver, timeout).until(
            EC.element_to_be_clickable((By.XPATH, xpath))
        )
        btn.click()
        print("  ✓ [Reading] 「採点」ボタンをクリックしました")
        delay = random.uniform(config.DELAY_MIN, config.DELAY_MAX)
        print(f"  [System] 採点後の読み込みを待機中... ({delay:.1f} 秒)")
        time.sleep(delay)
        return True
    except Exception:
        print("  ✗ [Reading] 「採点」ボタンが見つかりませんでした。")
        return False

def click_reading_quit(driver, timeout: int = 10) -> bool:
    """
    「終了」ボタン（quitButton）をクリックする。
    """
    print("\n  [Reading] 「終了」ボタンを検索中...")
    
    xpath = '//*[@id="quitButton"]'
    
    try:
        btn = WebDriverWait(driver, timeout).until(
            EC.element_to_be_clickable((By.XPATH, xpath))
        )
        btn.click()
        print("  ✓ [Reading] 「終了」ボタンをクリックしました")
        delay = random.uniform(config.DELAY_MIN, config.DELAY_MAX)
        print(f"  [System] 終了後の読み込みを待機中... ({delay:.1f} 秒)")
        time.sleep(delay)
        return True
    except Exception:
        print("  ✗ [Reading] 「終了」ボタンが見つかりませんでした。")
        return False

def click_reading_player_test(driver, timeout: int = 10) -> bool:
    """
    テストモード（本番）のプレイヤーリンクをクリックする。
    """
    print("\n  [Reading] テストモードのプレイヤーリンクを検索中...")
    xpath = '//*[@id="main-container"]/div[2]/div/div[4]/div/div[5]/div/div/div[1]/div[3]/a'
    
    try:
        elem = WebDriverWait(driver, timeout).until(
            EC.element_to_be_clickable((By.XPATH, xpath))
        )
        elem.click()
        print("  ✓ [Reading] テストモードに入りました")
        
        try:
            WebDriverWait(driver, timeout).until(EC.staleness_of(elem))
            print("  ✓ [Reading] テスト画面への遷移を完了しました")
        except Exception:
            pass
            
        return True
    except Exception:
        print("  ✗ [Reading] テストモードのリンクが見つかりませんでした。")
        return False

def solve_reading_test(driver, timeout: int = 10) -> bool:
    """
    保存した回答データを用いてテストを自動解答し、「次へ」ボタンを押す。
    """
    global _reading_extracted_answers
    if not _reading_extracted_answers:
        print("  ✗ [Reading] 保存された回答データがありません。")
        return False
        
    print("\n  [Reading] 自動解答を開始します...")
    
    # 抽出した答えの数だけループ
    for x in range(1, len(_reading_extracted_answers) + 1):
        target_answer = _reading_extracted_answers.get(x, "")
        print(f"  [Reading] 問題 {x} の正解を探します: {target_answer}")
        
        # y（選択肢番号）を探す
        matched = False
        for y in range(1, 10):
            # 選択肢の全体テキストを取得するXPath
            text_xpath = f'//*[@id="root"]/div/div/div[2]/div/div/div[3]/div/div/div[2]/div[2]/div/div[{x}]/div/div[3]/ul/li[{y}]'
            button_xpath = f'//*[@id="root"]/div/div/div[2]/div/div/div[3]/div/div/div[2]/div[2]/div/div[{x}]/div/div[3]/ul/li[{y}]/div/button'
            
            try:
                opt_elem = driver.find_elements(By.XPATH, text_xpath)
                if not opt_elem:
                    break # 選択肢がもう無い
                    
                opt_text = opt_elem[0].text.strip()
                
                # a. などのプレフィックスを取り除く
                for prefix in ['a. ', 'b. ', 'c. ', 'd. ', 'e. ', 'A. ', 'B. ', 'C. ', 'D. ', 'E. ']:
                    if opt_text.startswith(prefix):
                        opt_text = opt_text[len(prefix):].strip()
                        break
                        
                # 抽出したテキストと一致したらクリック
                if opt_text == target_answer or target_answer in opt_text:
                    btn = WebDriverWait(driver, 2).until(
                        EC.element_to_be_clickable((By.XPATH, button_xpath))
                    )
                    # スクロールしてクリック（画面外対策）
                    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", btn)
                    time.sleep(0.5)
                    btn.click()
                    print(f"  ✓ [Reading] 問題 {x}: 選択肢 {y} '{opt_text}' をクリックしました")
                    matched = True
                    time.sleep(1.0)
                    break
            except Exception as e:
                break
                
        if not matched:
            print(f"  ✗ [Reading] 問題 {x}: 一致する選択肢が見つかりませんでした。")
            
    # 全ての解答が終わったら次へボタンを押す
    try:
        next_btn = WebDriverWait(driver, timeout).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="nextButton"]'))
        )
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", next_btn)
        time.sleep(0.5)
        next_btn.click()
        print("  ✓ [Reading] 「次へ」ボタンをクリックしました")
        delay = random.uniform(config.DELAY_MIN, config.DELAY_MAX)
        print(f"  [System] 次への画面遷移を待機中... ({delay:.1f} 秒)")
        time.sleep(delay)
        return True
    except Exception:
        print("  ✗ [Reading] 「次へ」ボタンが見つかりませんでした。")
        return False

def run_reading_automation(driver, url: str):
    """
    Reading学習を自動化するエントリー関数。
    """
    print("\n========================================")
    print("  [System] Readingの自動学習処理を開始します")
    print("========================================")
    
    # 1. stlistボタンを押す
    clicked_stlist_1 = click_reading_stlist(driver, timeout=5)
    if not clicked_stlist_1: return
    time.sleep(random.uniform(config.DELAY_MIN, config.DELAY_MAX))
    
    # 2. stunitボタンを押す
    clicked_stunit_1 = click_reading_stunit(driver, timeout=5)
    if not clicked_stunit_1: return
    time.sleep(random.uniform(config.DELAY_MIN, config.DELAY_MAX))
    
    # 3. 一回元のURLに戻る
    driver.get(url)
    time.sleep(random.uniform(config.DELAY_MIN, config.DELAY_MAX))
    
    # 4. stlistボタンを押す
    clicked_stlist_2 = click_reading_stlist(driver, timeout=5)
    if not clicked_stlist_2: return
    time.sleep(random.uniform(config.DELAY_MIN, config.DELAY_MAX))
    
    # 5. stunitボタンを押す
    clicked_stunit_2 = click_reading_stunit(driver, timeout=5)
    if not clicked_stunit_2: return
    time.sleep(random.uniform(config.DELAY_MIN, config.DELAY_MAX))
    
    # 6. プレイヤーリンク(学習する)を押す
    clicked_player_1 = click_reading_player(driver, timeout=5)
    if not clicked_player_1: return
    time.sleep(random.uniform(config.DELAY_MIN, config.DELAY_MAX))
    
    # 7. 「採点」ボタン(confirmButton)を押す
    clicked_confirm = click_reading_confirm(driver, timeout=5)
    if not clicked_confirm: return
    time.sleep(random.uniform(config.DELAY_MIN, config.DELAY_MAX))
    
    # 8. 画像と回答データを抽出して保存
    extract_reading_data(driver, timeout=5)
    time.sleep(random.uniform(config.DELAY_MIN, config.DELAY_MAX))
    
    # 9. 「終了」ボタン(quitButton)を押す
    clicked_quit = click_reading_quit(driver, timeout=5)
    if not clicked_quit: return
    time.sleep(random.uniform(config.DELAY_MIN, config.DELAY_MAX))
    
    # 10. テストモードのプレイヤーリンクをクリック
    clicked_test_player = click_reading_player_test(driver, timeout=5)
    if not clicked_test_player: return
    time.sleep(random.uniform(config.DELAY_MIN, config.DELAY_MAX))
    
    # 11. 自動解答を実行し、「次へ」を押す
    solved = solve_reading_test(driver, timeout=5)
    if not solved: return
    time.sleep(random.uniform(config.DELAY_MIN, config.DELAY_MAX))
    
    print("  [Reading] (※ここに後ほどさらなるロジックがあれば追加します)")
        
    # 全て完了後に元のURLに戻る
    driver.get(url)
