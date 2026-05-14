from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import random
import os
import requests
import asyncio
import re
import difflib
from winrt.windows.media.ocr import OcrEngine
from winrt.windows.storage import StorageFile
from winrt.windows.graphics.imaging import BitmapDecoder
from winrt.windows.globalization import Language
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

def click_preliminary_choice(driver, timeout: int = 10) -> bool:
    """
    1周目の学習で、採点前に特定のボタン（予備選択）をクリックする。
    """
    print("\n  [Reading] 採点前の予備選択をクリック中...")
    xpath = '//*[@id="root"]/div/div/div[2]/div/div/div[3]/div/div/div[2]/div[2]/div/div[1]/div/div[3]/ul/li[1]/div/button'
    try:
        btn = WebDriverWait(driver, timeout).until(
            EC.element_to_be_clickable((By.XPATH, xpath))
        )
        btn.click()
        print("  ✓ [Reading] 予備選択をクリックしました")
        time.sleep(random.uniform(config.DELAY_MIN, config.DELAY_MAX))
        return True
    except Exception:
        print("  ✗ [Reading] 予備選択のボタンが見つかりませんでした。")
        return False

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

async def _perform_reading_ocr_async(image_path: str) -> str:
    """
    Windows組み込みOCRエンジンを使用して画像からテキストを抽出する。
    画像が英語であることを考慮し、en-USエンジンを使用する。
    """
    try:
        # 利用可能な言語を確認
        try:
            supported_langs = OcrEngine.get_available_recognizer_languages()
            lang_tags = [l.language_tag for l in supported_langs]
            print(f"  [Reading] 利用可能なOCR言語: {lang_tags}")
        except Exception:
            pass

        # 英語(en-US)エンジンを明示的に作成
        target_lang = "en-US"
        engine = None
        
        if OcrEngine.is_language_supported(Language(target_lang)):
            engine = OcrEngine.try_create_from_language(Language(target_lang))
            print(f"  [Reading] OCRエンジンを {target_lang} モードで起動しました")
        else:
            engine = OcrEngine.try_create_from_user_profile_languages()
            print(f"  [Reading] 警告: {target_lang} がサポートされていないため、システム言語を使用します")
        
        if not engine:
            return ""
        
        abs_path = os.path.abspath(image_path)
        file = await StorageFile.get_file_from_path_async(abs_path)
        stream = await file.open_async(0)
        decoder = await BitmapDecoder.create_async(stream)
        s_bitmap = await decoder.get_software_bitmap_async()
        
        result = await engine.recognize_async(s_bitmap)
        return result.text
    except Exception as e:
        print(f"  ✗ [Reading] OCR処理中にエラーが発生しました: {e}")
        return ""

def solve_reading_cloze(driver, ocr_text: str, timeout: int = 10) -> bool:
    """
    OCRで取得した全文テキストと、画面上のspan構造を照合して穴埋めを解く。
    """
    if not ocr_text:
        print("  ✗ [Reading] OCRテキストが空のため、穴埋めをスキップします。")
        return False

    base_xpath = '//*[@id="root"]/div/div/div[2]/div/div/div[3]/div/div/div[2]/span[{}]'
    
    spans_data = []
    x = 2
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
        print("  ✗ [Reading] 文章の構造(span)が見つかりませんでした。")
        return False
        
    # OCRテキストの正規化 (最低限の記号・ノイズ除去のみ)
    def normalize_for_match(t):
        if not t: return ""
        # 小文字化と記号の正規化
        t = t.lower()
        t = t.replace('|', 'l').replace('!', 'i').replace('$', 's').replace('(', 'c').replace(')', ' ')
        # 非ASCIIを排除
        t = "".join([c if (ord(c) < 128) else " " for c in t])
        # 連続スペースを統合
        t = re.sub(r'[\r\n\t\s]+', ' ', t).strip()
        return t

    def get_fuzzy_ratio(s1, s2):
        """文字列の構造類似度 (difflib)"""
        if not s1 or not s2: return 0.0
        return difflib.SequenceMatcher(None, s1, s2).ratio()

    normalized_ocr = normalize_for_match(ocr_text)
    ocr_words = normalized_ocr.split()
    print(f"  [Reading] OCR全文 (単語数: {len(ocr_words)}): {normalized_ocr}")

    normalized_ocr = normalize_for_match(ocr_text)
    ocr_words = normalized_ocr.split()
    print(f"  [Reading] OCR全文 (単語数: {len(ocr_words)}): {normalized_ocr}")

    def get_fuzzy_ratio(s1, s2):
        """2つの単語の類似度を 0.0~1.0 で返す。"""
        if s1 == s2: return 1.0
        if not s1 or not s2: return 0.0
        # 簡易的な編集距離の代用（共通文字数ベース）
        common = sum(1 for c in s1 if c in s2)
        return common / max(len(s1), len(s2))

    # 各inputについてスコアリングで場所を特定
    found_count = 0
    for i, item in enumerate(spans_data):
        if item["type"] == "input":
            x_idx = item["x"]
            
            # 周囲のアンカー単語を収集 (前後5単語)
            prev_anchors = []
            for j in range(i-1, -1, -1):
                if spans_data[j]["type"] == "text":
                    words = normalize_for_match(spans_data[j]["text"]).split()
                    prev_anchors.extend(reversed(words))
                    if len(prev_anchors) >= 5: break
            prev_anchors = prev_anchors[:5] # 近い順
            
            next_anchors = []
            for j in range(i+1, len(spans_data)):
                if spans_data[j]["type"] == "text":
                    words = normalize_for_match(spans_data[j]["text"]).split()
                    next_anchors.extend(words)
                    if len(next_anchors) >= 5: break
            next_anchors = next_anchors[:5] # 近い順
            
            print(f"  [Reading] input[{x_idx}] 探索開始 (前方アンカー: {prev_anchors[::-1]}, 後方アンカー: {next_anchors})")
            
            best_p = -1
            max_score = -1.0
            
            # 全単語位置を走査してスコア計算
            for p in range(len(ocr_words)):
                score = 0.0
                # 1. 前方アンカーの評価
                for k, anchor in enumerate(prev_anchors):
                    target_idx = p - 1 - k
                    if target_idx >= 0:
                        ratio = get_fuzzy_ratio(ocr_words[target_idx], anchor)
                        if ratio > 0.8:
                            score += (10.0 - k * 1.5) # 近いほど高得点 (10, 8.5, 7...)
                
                # 2. 後方アンカーの評価
                for k, anchor in enumerate(next_anchors):
                    target_idx = p + 1 + k
                    if target_idx < len(ocr_words):
                        ratio = get_fuzzy_ratio(ocr_words[target_idx], anchor)
                        if ratio > 0.8:
                            score += (10.0 - k * 1.5)
                
                # 3. 文頭・文末ボーナス
                if i == 0 and p == 0: score += 5.0 # 文章の最初
                if i == len(spans_data)-1 and p == len(ocr_words)-1: score += 5.0 # 文章の最後
                
                if score > max_score:
                    max_score = score
                    best_p = p
            
            # スコアが一定以上なら採用
            if max_score > 5.0:
                ans_text = ocr_words[best_p].strip('.,!?";:')
                print(f"  ✓ [Reading] input[{x_idx}] 特定成功 (スコア: {max_score:.1f}, 単語: '{ans_text}')")
                
                input_xpath = base_xpath.format(x_idx) + '//input'
                try:
                    inp = driver.find_element(By.XPATH, input_xpath)
                    inp.clear()
                    inp.send_keys(ans_text)
                    found_count += 1
                    time.sleep(0.3)
                except Exception as e:
                    print(f"  ✗ [Reading] input[{x_idx}] の入力に失敗しました: {e}")
            else:
                print(f"  ✗ [Reading] input[{x_idx}] の一致箇所が見つかりませんでした (最高スコア: {max_score:.1f})")
    
    return found_count > 0

def click_reading_next(driver, timeout: int = 10) -> bool:
    """
    「次へ」ボタン（nextButton）をクリックする。
    """
    try:
        btn = WebDriverWait(driver, timeout).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="nextButton"]'))
        )
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", btn)
        time.sleep(0.5)
        btn.click()
        print("  ✓ [Reading] 「次へ」ボタンをクリックしました")
        time.sleep(random.uniform(config.DELAY_MIN, config.DELAY_MAX))
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
    
    # 7. 採点前に予備選択をクリック
    click_preliminary_choice(driver, timeout=5)
    
    # 8. 「採点」ボタン(confirmButton)を押す
    clicked_confirm = click_reading_confirm(driver, timeout=5)
    if not clicked_confirm: return
    time.sleep(random.uniform(config.DELAY_MIN, config.DELAY_MAX))
    
    # 9. 画像と回答データを抽出して保存
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
    
    # 12. OCRを実行
    img_path = './temp/reading_image.png'
    ocr_text = ""
    
    if os.path.exists(img_path):
        print(f"  [Reading] 画像解析を開始: {os.path.basename(img_path)}")
        ocr_text = asyncio.run(_perform_reading_ocr_async(img_path))
    else:
        print(f"  ✗ [Reading] 解析対象の画像が見つかりません。")
    
    # 13. 穴埋め問題を繰り返す（「次へ」が押せる限り継続）
    round_idx = 1
    while True:
        print(f"\n  [Reading] 穴埋めセクション {round_idx} を実行中...")
        if ocr_text:
            solve_reading_cloze(driver, ocr_text)
        
        time.sleep(random.uniform(config.DELAY_MIN, config.DELAY_MAX))
        
        # 「次へ」ボタンがあるか確認
        if click_reading_next(driver, timeout=3):
            # 押せたら次のラウンドへ
            round_idx += 1
            continue
        else:
            # 押せなくなったら「採点」して終了
            print(f"  [Reading] 「次へ」ボタンがないため、最終セクションと判断して採点します。")
            click_reading_confirm(driver, timeout=5)
            break
        
    # 全て完了後に元のURLに戻る
    driver.get(url)
