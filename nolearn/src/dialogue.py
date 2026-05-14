from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import random
import re
import src.config as config

# --- メモリ上へのデータ保存用変数 ---
_dialogue_extracted_script = ""
_dialogue_extracted_answers = {}

def click_dialogue_stunit(driver, timeout: int = 10) -> bool:
    """
    Dialogueの「stunit」ボタンをクリックする。
    hrefに "/listening/stunit/" を含むボタンを探す。
    """
    print("\n  [Dialogue] 「stunit」ボタンを検索中...")
    
    selector = 'a[href*="/listening/stunit/"].btn_listening'
    
    try:
        elem = WebDriverWait(driver, timeout).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
        )
        elem.click()
        print("  ✓ [Dialogue] 「stunit」ボタンをクリックしました")
        
        # 遷移中を待機
        try:
            WebDriverWait(driver, timeout).until(EC.staleness_of(elem))
            print("  ✓ [Dialogue] 画面遷移を完了しました")
        except Exception:
            pass
            
        return True
    except Exception:
        print("  ✗ [Dialogue] 「stunit」ボタンが見つからないか、クリック不可です。")
        return False

def click_dialogue_stlist(driver, timeout: int = 10) -> bool:
    """
    Dialogueの「stlist」ボタンをクリックする。
    hrefに "/listening/stlist/" を含むボタンを探す。
    """
    print("\n  [Dialogue] 「stlist」ボタンを検索中...")
    
    selector = 'a[href*="/listening/stlist/"].btn_listening'
    
    try:
        elem = WebDriverWait(driver, timeout).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
        )
        elem.click()
        print("  ✓ [Dialogue] 「stlist」ボタンをクリックしました")
        
        # 遷移中を待機
        try:
            WebDriverWait(driver, timeout).until(EC.staleness_of(elem))
            print("  ✓ [Dialogue] 画面遷移を完了しました")
        except Exception:
            pass
            
        return True
    except Exception:
        print("  ✗ [Dialogue] 「stlist」ボタンが見つからないか、クリック不可です。")
        return False

def click_dialogue_player(driver, timeout: int = 10) -> bool:
    """
    Dialogueのプレイヤーリンク（学習する）をクリックする。
    指定されたXPathを厳密に使用する。
    """
    print("\n  [Dialogue] 「学習する」プレイヤーリンクを検索中...")
    
    xpath = '//*[@id="main-container"]/div[2]/div/div[4]/div/div[4]/div/div/div[1]/div[3]/a'
    
    try:
        elem = WebDriverWait(driver, timeout).until(
            EC.element_to_be_clickable((By.XPATH, xpath))
        )
        elem.click()
        print("  ✓ [Dialogue] 「学習する」をクリックしました")
        
        try:
            WebDriverWait(driver, timeout).until(EC.staleness_of(elem))
            print("  ✓ [Dialogue] プレイヤー画面への遷移を完了しました")
        except Exception:
            pass
            
        return True
    except Exception:
        print("  ✗ [Dialogue] 「学習する」プレイヤーリンクが見つかりませんでした。")
        return False

def type_space_in_dialogue(driver, timeout: int = 10) -> bool:
    """
    採点を押す前にテキストボックスに半角スペースを入力する。
    """
    print("\n  [Dialogue] テキストボックスに <space> を入力します...")
    xpath = '//*[@id="root"]/div/div/div[2]/div/div/div[3]/div/div/div[2]/div[2]/div/div[5]/div/div[2]/span[2]/input'
    
    try:
        elem = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.XPATH, xpath))
        )
        elem.clear()
        elem.send_keys(" ")
        print("  ✓ [Dialogue] テキストボックスに <space> を入力しました")
        return True
    except Exception:
        print("  ✗ [Dialogue] テキストボックスが見つかりませんでした。")
        return False

def click_dialogue_confirm(driver, timeout: int = 10) -> bool:
    """
    「採点」ボタン（confirmButton）をクリックする。
    """
    print("\n  [Dialogue] 「採点」ボタンを検索中...")
    
    xpath = '//*[@id="confirmButton"]'
    
    try:
        btn = WebDriverWait(driver, timeout).until(
            EC.element_to_be_clickable((By.XPATH, xpath))
        )
        btn.click()
        print("  ✓ [Dialogue] 「採点」ボタンをクリックしました")
        delay = random.uniform(config.DELAY_MIN, config.DELAY_MAX)
        print(f"  [System] 採点後の読み込みを待機中... ({delay:.1f} 秒)")
        time.sleep(delay)
        return True
    except Exception:
        print("  ✗ [Dialogue] 「採点」ボタンが見つかりませんでした。")
        return False

def extract_dialogue_data(driver, timeout: int = 10) -> bool:
    """
    終了ボタンを押す前に、英語のスクリプトと選択肢の文字列を抽出してメモリ上に保存する。
    """
    global _dialogue_extracted_script, _dialogue_extracted_answers
    print("\n  [Dialogue] スクリプトと回答の文字列を抽出中...")
    
    # 1. スクリプトの抽出
    script_xpath = '//*[@id="root"]/div/div/div[2]/div/div/div[3]/div[3]/div/table[2]/tbody/tr[1]/td/div/div[2]/div[2]/div[2]'
    try:
        script_elem = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.XPATH, script_xpath))
        )
        _dialogue_extracted_script = script_elem.text
        print("  ✓ [Dialogue] スクリプトを抽出しました")
        # 先頭部分だけログに表示
        preview = _dialogue_extracted_script[:30].replace('\n', ' ') + "..." if len(_dialogue_extracted_script) > 30 else _dialogue_extracted_script
        print(f"    -> {preview}")
    except Exception:
        print("  ✗ [Dialogue] スクリプトの抽出に失敗しました。")
        _dialogue_extracted_script = ""
        
    # 2. 回答の文字列の抽出
    _dialogue_extracted_answers.clear()
    base_xpath = '//*[@id="root"]/div/div/div[2]/div/div/div[3]/div[3]/div/table[2]/tbody/tr[{}]/td[3]/div[1]/div[4]/div[2]'
    
    # x は 2, 3, 4, 5 (回答1, 2, 3, 4)
    for x in range(2, 6):
        ans_num = x - 1
        xpath = base_xpath.format(x)
        try:
            ans_elem = WebDriverWait(driver, 2).until(
                EC.presence_of_element_located((By.XPATH, xpath))
            )
            text = ans_elem.text.strip()
            # 'a. ', 'b. ' などのプレフィックスを削除
            for prefix in ['a. ', 'b. ', 'c. ', 'd. ', 'e. ']:
                if text.startswith(prefix):
                    text = text[len(prefix):]
                    break
                    
            _dialogue_extracted_answers[ans_num] = text
            print(f"  ✓ [Dialogue] 回答 {ans_num}: {text}")
        except Exception:
            break
            
    # 回答5 (tr[6]) の特別抽出
    ans5_xpath = '//*[@id="root"]/div/div/div[2]/div/div/div[3]/div[3]/div/table[2]/tbody/tr[6]/td[3]/div[1]/div[3]/div/div[2]/span'
    try:
        ans5_elem = WebDriverWait(driver, 2).until(
            EC.presence_of_element_located((By.XPATH, ans5_xpath))
        )
        text5 = ans5_elem.text.strip()
        # プレフィックスを削除
        for prefix in ['a. ', 'b. ', 'c. ', 'd. ', 'e. ']:
            if text5.startswith(prefix):
                text5 = text5[len(prefix):]
                break
                
        _dialogue_extracted_answers[5] = text5
        print(f"  ✓ [Dialogue] 回答 5: {text5}")
    except Exception:
        print("  ✗ [Dialogue] 回答 5 の抽出に失敗しました。")
            
    return True

def click_dialogue_quit(driver, timeout: int = 10) -> bool:
    """
    「終了」ボタン（quitButton）をクリックする。
    """
    print("\n  [Dialogue] 「終了」ボタンを検索中...")
    
    xpath = '//*[@id="quitButton"]'
    
    try:
        btn = WebDriverWait(driver, timeout).until(
            EC.element_to_be_clickable((By.XPATH, xpath))
        )
        btn.click()
        print("  ✓ [Dialogue] 「終了」ボタンをクリックしました")
        delay = random.uniform(config.DELAY_MIN, config.DELAY_MAX)
        print(f"  [System] 終了後の読み込みを待機中... ({delay:.1f} 秒)")
        time.sleep(delay)
        return True
    except Exception:
        print("  ✗ [Dialogue] 「終了」ボタンが見つかりませんでした。")
        return False

def click_dialogue_next(driver, timeout: int = 10) -> bool:
    """
    「次へ」ボタン（nextButton）をクリックする。
    """
    print("\n  [Dialogue] 「次へ」ボタンを検索中...")
    
    xpath = '//*[@id="nextButton"]'
    
    try:
        btn = WebDriverWait(driver, timeout).until(
            EC.element_to_be_clickable((By.XPATH, xpath))
        )
        btn.click()
        print("  ✓ [Dialogue] 「次へ」ボタンをクリックしました")
        delay = random.uniform(config.DELAY_MIN, config.DELAY_MAX)
        print(f"  [System] 次へボタン後の読み込みを待機中... ({delay:.1f} 秒)")
        time.sleep(delay)
        return True
    except Exception:
        print("  ✗ [Dialogue] 「次へ」ボタンが見つかりませんでした。")
        return False

def click_dialogue_player_test(driver, timeout: int = 10) -> bool:
    """
    テストモード（本番）のプレイヤーリンクをクリックする。
    """
    print("\n  [Dialogue] テストモードのプレイヤーリンクを検索中...")
    xpath = '//*[@id="main-container"]/div[2]/div/div[4]/div/div[6]/div/div/div[1]/div[3]/a'
    
    try:
        elem = WebDriverWait(driver, timeout).until(
            EC.element_to_be_clickable((By.XPATH, xpath))
        )
        elem.click()
        print("  ✓ [Dialogue] テストモードに入りました")
        
        try:
            WebDriverWait(driver, timeout).until(EC.staleness_of(elem))
            print("  ✓ [Dialogue] テスト画面への遷移を完了しました")
        except Exception:
            pass
            
        return True
    except Exception:
        print("  ✗ [Dialogue] テストモードのリンクが見つかりませんでした。")
        return False

def solve_dialogue_test(driver, timeout: int = 10) -> bool:
    """
    保存した解答データを使って、1番から5番までの問題を解く。
    """
    global _dialogue_extracted_answers
    print("\n  [Dialogue] テストモードの解答を入力します...")
    
    base_xpath = '//*[@id="root"]/div/div/div[2]/div/div/div[3]/div/div/div[2]/div[2]/div/div[{}]/div/div[3]/ul/li[{}]'
    
    for x in range(1, 6):
        target_ans = _dialogue_extracted_answers.get(x, "")
        if not target_ans:
            print(f"  [Dialogue] 問題 {x} の正解データがありません。スキップします。")
            continue
            
        print(f"  [Dialogue] 問題 {x} (正解: {target_ans}) を処理中...")
        
        if x == 5:
            # x=5 の時は input
            try:
                # ユーザー指定の正確な XPath
                input_xpath = '//*[@id="root"]/div/div/div[2]/div/div/div[3]/div/div/div[2]/div[2]/div/div[5]/div/div[2]/span[2]/input'
                input_elem = WebDriverWait(driver, 2).until(
                    EC.presence_of_element_located((By.XPATH, input_xpath))
                )
                input_elem.clear()
                input_elem.send_keys(target_ans)
                print("  ✓ [Dialogue] 問題 5 にテキストを入力しました")
                time.sleep(1)
            except Exception as e:
                print(f"  ✗ [Dialogue] 問題 5 の入力に失敗しました: {e}")
            continue
        answered = False
        for y in range(1, 6):
            xpath = base_xpath.format(x, y)
            try:
                # 存在確認 (タイムアウト短め)
                elem = WebDriverWait(driver, 1).until(
                    EC.presence_of_element_located((By.XPATH, xpath))
                )
                text = elem.text.strip()
                
                # プレフィックス除去
                clean_text = text
                for prefix in ['a. ', 'b. ', 'c. ', 'd. ', 'e. ', 'A. ', 'B. ', 'C. ', 'D. ', 'E. ']:
                    if clean_text.startswith(prefix):
                        clean_text = clean_text[len(prefix):].strip()
                        break
                        
                # 大文字小文字無視で部分一致か確認
                if target_ans.lower() in clean_text.lower() or clean_text.lower() in target_ans.lower():
                    try:
                        elem.click()
                    except:
                        driver.execute_script("arguments[0].click();", elem)
                        
                    print(f"  ✓ [Dialogue] 問題 {x}: 選択肢 {y} ({text}) を選択しました")
                    answered = True
                    time.sleep(1)
                    break
            except Exception:
                # 要素がなければループを抜ける
                break
                
        if not answered and x != 5:
            print(f"  ✗ [Dialogue] 問題 {x} の一致する選択肢が見つかりませんでした。")
            
    return True

def solve_dialogue_cloze(driver, timeout: int = 10) -> bool:
    """
    保存したスクリプトと穴埋めテキストを照合し、差分から解答を割り出して入力する。
    """
    global _dialogue_extracted_script
    print("\n  [Dialogue] 穴埋め(Cloze)テストの解答を計算して入力します...")
    
    if not _dialogue_extracted_script:
        print("  ✗ [Dialogue] 元のスクリプトが保存されていないため、穴埋めができません。")
        return False
        
    base_xpath = '//*[@id="root"]/div/div/div[2]/div/div/div[3]/div/div/div[3]/span[{}]'
    
    spans_data = []
    x = 1
    while True:
        xpath = base_xpath.format(x)
        try:
            span_elem = WebDriverWait(driver, 0.5).until(
                EC.presence_of_element_located((By.XPATH, xpath))
            )
            inputs = span_elem.find_elements(By.TAG_NAME, 'input')
            if inputs:
                spans_data.append({"type": "input", "x": x})
            else:
                text = span_elem.text
                spans_data.append({"type": "text", "text": text})
            x += 1
        except Exception:
            break
            
    if not spans_data:
        print("  ✗ [Dialogue] 文章の構造(span)が見つかりませんでした。")
        return False
        
    print(f"  [Dialogue] {len(spans_data)} 個の穴埋め構造を取得しました。照合中...")
    
    regex_parts = []
    for item in spans_data:
        if item["type"] == "text":
            txt = item["text"].strip()
            if not txt:
                continue
            escaped = re.escape(txt)
            escaped = escaped.replace(r'\ ', ' ')
            escaped = escaped.replace(' ', r'\s*')
            regex_parts.append(escaped)
        else:
            # inputの部分は、spanのインデックス(x)を名前として持つキャプチャグループにする
            # 連続inputの誤爆を防ぐため (\S+) を使用しつつ、xの値で一意に紐付ける
            x_idx = item["x"]
            regex_parts.append(rf'(?P<input_{x_idx}>\S+)')
            
    pattern_str = r'\s*'.join(regex_parts)
    pattern_str = r'^.*?' + pattern_str + r'.*?$'
    
    normalized_script = re.sub(r'\s+', ' ', _dialogue_extracted_script).strip()
    
    match = re.search(pattern_str, normalized_script, re.IGNORECASE | re.DOTALL)
    
    if match:
        print(f"  ✓ [Dialogue] 正規表現マッチ成功！")
        
        input_items = [item for item in spans_data if item["type"] == "input"]
        for item in input_items:
            x_idx = item["x"]
            try:
                # 名前付きキャプチャグループ(input_{x})から、直接対応するテキストを取得
                ans_text = match.group(f"input_{x_idx}")
            except IndexError:
                print(f"  ✗ [Dialogue] 穴埋め(x={x_idx})の解答が見つかりません。")
                continue
                
            ans_text = ans_text.strip()
            # 抽出した単語から末尾や先頭の記号を削除（純粋な単語のみにする）
            ans_text = ans_text.strip('.,!?";:')
            
            input_xpath = base_xpath.format(x_idx) + '//input'
            try:
                inp = driver.find_element(By.XPATH, input_xpath)
                inp.clear()
                inp.send_keys(ans_text)
                print(f"  ✓ [Dialogue] 穴埋め (span[{x_idx}]) に '{ans_text}' を入力しました")
                time.sleep(0.3)
            except Exception as e:
                print(f"  ✗ [Dialogue] 穴埋め (span[{x_idx}]) の入力に失敗しました: {e}")
    else:
        print("  ✗ [Dialogue] パターンマッチに失敗しました。元のスクリプトと構造が合致しません。")
        return False
        
    return True

def run_dialogue_automation(driver, url: str):
    """
    Dialogue学習を自動化するエントリー関数。
    現在は学習開始ボタンのクリックのみ実行する。
    """
    print("\n========================================")
    print("  [System] Dialogueの自動学習処理を開始します")
    print("========================================")
    
    # 1. stlistボタンを押す
    clicked_stlist_1 = click_dialogue_stlist(driver, timeout=5)
    if not clicked_stlist_1: return
    time.sleep(random.uniform(config.DELAY_MIN, config.DELAY_MAX))
    
    # 2. stunitボタンを押す
    clicked_stunit_1 = click_dialogue_stunit(driver, timeout=5)
    if not clicked_stunit_1: return
    time.sleep(random.uniform(config.DELAY_MIN, config.DELAY_MAX))
    
    # 3. 一回元のURLに戻る
    driver.get(url)
    time.sleep(random.uniform(config.DELAY_MIN, config.DELAY_MAX))
    
    # 4. stlistボタンを押す
    clicked_stlist_2 = click_dialogue_stlist(driver, timeout=5)
    if not clicked_stlist_2: return
    time.sleep(random.uniform(config.DELAY_MIN, config.DELAY_MAX))
    
    # 5. stunitボタンを押す
    clicked_stunit_2 = click_dialogue_stunit(driver, timeout=5)
    if not clicked_stunit_2: return
    time.sleep(random.uniform(config.DELAY_MIN, config.DELAY_MAX))
        
    # 6. プレイヤーリンクを押す
    clicked_player_1 = click_dialogue_player(driver, timeout=5)
    if not clicked_player_1: return
    time.sleep(random.uniform(config.DELAY_MIN, config.DELAY_MAX))
        
    # テキストボックスにスペースを入力
    type_space_in_dialogue(driver, timeout=5)
        
    # 10. 「採点」ボタン(confirmButton)を押す
    clicked_confirm_1 = click_dialogue_confirm(driver, timeout=10)
    if not clicked_confirm_1: return
    time.sleep(random.uniform(config.DELAY_MIN, config.DELAY_MAX))

    # [追加] 終了ボタンを押す前に情報を抽出してメモリに保存
    extract_dialogue_data(driver, timeout=5)

    # 7. 「終了」ボタン(quitButton)を押す
    clicked_quit_1 = click_dialogue_quit(driver, timeout=5)
    if not clicked_quit_1: return
    time.sleep(random.uniform(config.DELAY_MIN, config.DELAY_MAX))
        
    # --- 新規: テストモード(div[6])への移行 ---
    # 8. テストモードのプレイヤーリンクをクリック
    clicked_test_player = click_dialogue_player_test(driver, timeout=5)
    if not clicked_test_player: return
    time.sleep(random.uniform(config.DELAY_MIN, config.DELAY_MAX))
    
    # 9. 解答を入力
    solve_dialogue_test(driver, timeout=10)
    time.sleep(random.uniform(config.DELAY_MIN, config.DELAY_MAX))
    
    # 11. 「次へ」ボタン(nextButton)を押す (終了ボタンの代わり)
    click_dialogue_next(driver, timeout=5)
    time.sleep(random.uniform(config.DELAY_MIN, config.DELAY_MAX))
    
    # 12. 穴埋め(Cloze)テストの解答
    solve_dialogue_cloze(driver, timeout=10)
    time.sleep(random.uniform(config.DELAY_MIN, config.DELAY_MAX))
    
    # 13. 「採点」ボタン(confirmButton)を再度押す
    click_dialogue_confirm(driver, timeout=10)
    time.sleep(random.uniform(config.DELAY_MIN, config.DELAY_MAX))
    
    # 14. 全て完了後に元のURLに戻る
    print("\n  [Dialogue] 処理が完了しました。元のURLに戻ります...")
    driver.get(url)
