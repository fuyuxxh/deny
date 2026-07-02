from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
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
_reading_extracted_text = ""
_reading_isinsert = False

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

def check_insert_button(driver, timeout: int = 5) -> bool:
    """
    insertボタン（指定XPath）を探し、見つかったらクリックしてTrueを返す。
    見つからなければFalseを返す。
    """
    print("\n  [Reading] insertボタンを検索中...")
    xpath = '//*[@id="root"]/div/div/div[2]/div/div/div[4]/button'
    
    try:
        btn = WebDriverWait(driver, timeout).until(
            EC.element_to_be_clickable((By.XPATH, xpath))
        )
        btn.click()
        print("  ✓ [Reading] insertボタンをクリックしました (Isinsert = True)")
        return True
    except Exception:
        print("  ✗ [Reading] insertボタンが見つかりませんでした (Isinsert = False)")
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
    global _reading_extracted_answers, _reading_isinsert
    print("\n  [Reading] 画像と回答の文字列を抽出中...")
    
    # 1. 画像のダウンロード（Isinsert = False の場合のみ）
    if not _reading_isinsert:
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
    else:
        print("  [Reading] Isinsert = True のため、画像抽出をスキップします")
        
    # 2. 回答の文字列の抽出
    _reading_extracted_answers.clear()
    
    # x = 2, 3, 4, 5, 6
    for x in range(2, 7):
        ans_num = x - 1 # 1, 2, 3, 4, 5 として保存
        ans_type = "choice"
        xpath_choice = f'//*[@id="root"]/div/div/div[2]/div/div/div[3]/div[3]/div/table[2]/tbody/tr[{x}]/td[3]/div[1]/div[4]/div[2]'
        xpath_text = f'//*[@id="root"]/div/div/div[2]/div/div/div[3]/div[3]/div/table[2]/tbody/tr[{x}]/td[3]/div[1]/div[3]/div/div[2]/span'
        
        try:
            ans_elem = WebDriverWait(driver, 1.5).until(
                EC.presence_of_element_located((By.XPATH, xpath_choice))
            )
            text = ans_elem.text.strip()
            
            if "(未回答)" in text or "(未解答)" in text:
                text_elem = driver.find_element(By.XPATH, xpath_text)
                text = text_elem.text.strip()
                ans_type = "text"
            
            # プレフィックスを削除
            for prefix in ['a. ', 'b. ', 'c. ', 'd. ', 'e. ', 'A. ', 'B. ', 'C. ', 'D. ', 'E. ']:
                if text.startswith(prefix):
                    text = text[len(prefix):].strip()
                    break
                    
            _reading_extracted_answers[ans_num] = {"text": text, "type": ans_type}
            print(f"  ✓ [Reading] 回答 {ans_num}: {text} (タイプ: {ans_type})")
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
    for x in range(1, 6):
        ans_info = _reading_extracted_answers.get(x, None)
        if not ans_info:
            print(f"  [Reading] 問題 {x} の正解データがありません。スキップします。")
            continue
            
        target_answer = ans_info["text"]
        ans_type = ans_info["type"]
        
        print(f"  [Reading] 問題 {x} の正解を探します: {target_answer} (タイプ: {ans_type})")
        
        if ans_type == "text":
            # テキスト入力方式
            try:
                # 動的に x 番目の input 要素を取得して入力する
                input_xpath = f'//*[@id="root"]/div/div/div[2]/div/div/div[3]/div/div/div[2]/div[2]/div/div[{x}]//input'
                input_elem = WebDriverWait(driver, 2).until(
                    EC.presence_of_element_located((By.XPATH, input_xpath))
                )
                input_elem.clear()
                input_elem.send_keys(target_answer)
                print(f"  ✓ [Reading] 問題 {x} にテキストを入力しました")
                time.sleep(1.0)
            except Exception as e:
                print(f"  ✗ [Reading] 問題 {x} の入力に失敗しました: {e}")
            continue
            
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

def run_reading_automation(driver, url: str) -> bool:
    """
    Reading学習を自動化するエントリー関数。
    Isinsertの値を返す（True: insertボタンあり, False: なし）。
    """
    print("\n========================================")
    print("  [System] Readingの自動学習処理を開始します")
    print("========================================")
    
    # 1. stlistボタンを押す
    clicked_stlist_1 = click_reading_stlist(driver, timeout=5)
    if not clicked_stlist_1: return False
    time.sleep(random.uniform(config.DELAY_MIN, config.DELAY_MAX))
    
    # 2. stunitボタンを押す
    clicked_stunit_1 = click_reading_stunit(driver, timeout=5)
    if not clicked_stunit_1: return False
    time.sleep(random.uniform(config.DELAY_MIN, config.DELAY_MAX))
    
    # 3. insertボタンの確認（URL戻りの前に実行）
    global _reading_isinsert
    Isinsert = check_insert_button(driver, timeout=5)
    time.sleep(random.uniform(config.DELAY_MIN, config.DELAY_MAX))
    
    # 4. 一回元のURLに戻る
    driver.get(url)
    time.sleep(random.uniform(config.DELAY_MIN, config.DELAY_MAX))
    
    # 5. stlistボタンを押す
    clicked_stlist_2 = click_reading_stlist(driver, timeout=5)
    if not clicked_stlist_2: return False
    time.sleep(random.uniform(config.DELAY_MIN, config.DELAY_MAX))
    
    # 6. stunitボタンを押す
    clicked_stunit_2 = click_reading_stunit(driver, timeout=5)
    if not clicked_stunit_2: return False
    time.sleep(random.uniform(config.DELAY_MIN, config.DELAY_MAX))
    
    # 6.5. 確認テストボタンの存在確認でIsinsertを判定（div[x]の最大を探索）
    print("\n  [Reading] 確認テストボタンの存在を確認中...")
    test_btn_found = False
    found_div_idx = -1
    for div_idx in range(10, 0, -1):
        test_btn_xpath = f'//*[@id="main-container"]/div[2]/div/div[4]/div/div[{div_idx}]/div/div/div[1]/div[3]/a'
        try:
            WebDriverWait(driver, 1).until(
                EC.presence_of_element_located((By.XPATH, test_btn_xpath))
            )
            test_btn_found = True
            found_div_idx = div_idx
            print(f"  ✓ [Reading] 確認テストボタンが見つかりました (div[{div_idx}])")
            break
        except Exception:
            continue
            
    if test_btn_found and found_div_idx >= 6:
        Isinsert = True
        _reading_isinsert = True
        print(f"  [Reading] div[{found_div_idx}] >= 6 のため Isinsert = True")
    else:
        Isinsert = False
        _reading_isinsert = False
        if test_btn_found:
            print(f"  [Reading] div[{found_div_idx}] <= 5 のため Isinsert = False")
        else:
            print("  ✗ [Reading] 確認テストボタンが見つかりませんでした (Isinsert = False)")
    time.sleep(random.uniform(config.DELAY_MIN, config.DELAY_MAX))
    
    # 7. プレイヤーリンク(学習する)を押す
    clicked_player_1 = click_reading_player(driver, timeout=5)
    if not clicked_player_1: return False
    time.sleep(random.uniform(config.DELAY_MIN, config.DELAY_MAX))
    
    if not Isinsert:
        # --- Isinsert = False の場合のみ、確認テスト解答処理を実行 ---
        print("\n  [Reading] Isinsert = False: 確認テスト解答処理を実行します")
        
        # 8. 採点前に予備選択をクリック
        click_preliminary_choice(driver, timeout=5)
        
        # 9. 「採点」ボタン(confirmButton)を押す
        clicked_confirm = click_reading_confirm(driver, timeout=5)
        if not clicked_confirm: return False
        time.sleep(random.uniform(config.DELAY_MIN, config.DELAY_MAX))
        
        # 10. 画像と回答データを抽出して保存
        extract_reading_data(driver, timeout=5)
        time.sleep(random.uniform(config.DELAY_MIN, config.DELAY_MAX))
        
        # 11. 「終了」ボタン(quitButton)を押す
        clicked_quit = click_reading_quit(driver, timeout=5)
        if not clicked_quit: return False
        time.sleep(random.uniform(config.DELAY_MIN, config.DELAY_MAX))
        
        # 12. テストモードのプレイヤーリンクをクリック
        clicked_test_player = click_reading_player_test(driver, timeout=5)
        if not clicked_test_player: return False
        time.sleep(random.uniform(config.DELAY_MIN, config.DELAY_MAX))
        
        # 13. 自動解答を実行し、「次へ」を押す
        solved = solve_reading_test(driver, timeout=5)
        if not solved: return False
        time.sleep(random.uniform(config.DELAY_MIN, config.DELAY_MAX))
        
        # 14. OCRを実行
        img_path = './temp/reading_image.png'
        ocr_text = ""
        
        if os.path.exists(img_path):
            print(f"  [Reading] 画像解析を開始: {os.path.basename(img_path)}")
            ocr_text = asyncio.run(_perform_reading_ocr_async(img_path))
        else:
            print(f"  ✗ [Reading] 解析対象の画像が見つかりません。")
        
        # 15. 穴埋め問題を繰り返す（「次へ」が押せる限り継続）
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
    else:
        # --- Isinsert = True の場合の処理 ---
        print("\n  [Reading] Isinsert = True: 確認テスト解答処理を実行します")
        
        # 8. 採点前に予備選択をクリック
        click_preliminary_choice(driver, timeout=5)
        
        # 9. 「採点」ボタン(confirmButton)を押す
        clicked_confirm = click_reading_confirm(driver, timeout=5)
        if not clicked_confirm: return False
        time.sleep(random.uniform(config.DELAY_MIN, config.DELAY_MAX))
        
        # 10. 文章と回答データを抽出してメモリに保存
        global _reading_extracted_text
        print("\n  [Reading] 文章を抽出中...")
        text_xpath = '//*[@id="root"]/div/div/div[2]/div/div/div[3]/div[3]/div/table[2]/tbody/tr[1]/td/div/div[2]/div[1]/div/div'
        try:
            text_elem = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, text_xpath))
            )
            _reading_extracted_text = text_elem.text.strip()
            if _reading_extracted_text:
                print(f"  ✓ [Reading] 文章を保存しました")
                print(f"  [Reading] 内容:\n{_reading_extracted_text}")
            else:
                print("  ✗ [Reading] 文章が空でした。")
        except Exception as e:
            print(f"  ✗ [Reading] 文章の抽出に失敗しました: {e}")
        # 文章抽出のみを行い、回答データ(選択肢)の抽出・保存(extract_reading_data)は行わない
        
        # 11. 「終了」ボタン(quitButton)を押す
        clicked_quit = click_reading_quit(driver, timeout=5)
        if not clicked_quit: return False
        time.sleep(random.uniform(config.DELAY_MIN, config.DELAY_MAX))
        
        # 12. 確認テストボタンをクリック（div[x]の最大を探索）
        print("\n  [Reading] 確認テストボタンをクリック中...")
        test_btn = None
        for div_idx in range(10, 0, -1):
            test_btn_xpath = f'//*[@id="main-container"]/div[2]/div/div[4]/div/div[{div_idx}]/div/div/div[1]/div[3]/a'
            try:
                test_btn = WebDriverWait(driver, 1).until(
                    EC.element_to_be_clickable((By.XPATH, test_btn_xpath))
                )
                print(f"  [Reading] 確認テストボタンを div[{div_idx}] で発見")
                break
            except Exception:
                continue
        if test_btn:
            try:
                test_btn.click()
                print("  ✓ [Reading] 確認テストボタンをクリックしました")
                try:
                    WebDriverWait(driver, 10).until(EC.staleness_of(test_btn))
                    print("  ✓ [Reading] 確認テスト画面への遷移を完了しました")
                except Exception:
                    pass
            except Exception as e:
                print(f"  ✗ [Reading] 確認テストボタンのクリックに失敗しました: {e}")
                return False
        else:
            print("  ✗ [Reading] 確認テストボタンが見つかりませんでした")
            return False
        time.sleep(random.uniform(config.DELAY_MIN, config.DELAY_MAX))
        
        # 13. 穴埋め問題の自動回答
        print("\n  [Reading] 穴埋め問題の自動回答を開始...")
        
        # 穴埋め箇所（クリック可能なspan）を全て取得
        insertion_spans = driver.find_elements(
            By.CSS_SELECTOR, 'span[class*="InsertionQuestionBuilder__insertionPosition"]'
        )
        n_blanks = len(insertion_spans)
        print(f"  [Reading] 穴埋め箇所: {n_blanks} 個")
        
        if n_blanks > 0 and _reading_extracted_text:
            # 最初の空白をクリックして選択肢を取得し、全文中の出現順でソート
            print("\n  [Reading] 選択肢を取得するため最初の空白をクリック...")
            driver.execute_script("arguments[0].click();", insertion_spans[0])
            time.sleep(2)
            
            # 選択肢のリストを取得（ダイアログ内のinsertChoiceクラスのspan）
            choice_elems = driver.find_elements(
                By.CSS_SELECTOR, 'span[class*="InsertionQuestionBuilder__insertChoice"]'
            )
            
            choices = []
            for elem in choice_elems:
                text = elem.text.strip()
                if text:
                    choices.append(text)
            
            # 重複を除去（同じテキストの選択肢がある場合）
            choices = list(dict.fromkeys(choices))
            
            print(f"  [Reading] 選択肢 ({len(choices)} 個): {choices}")
            
            # 全文中の出現順にソート
            def get_position_in_text(choice_text):
                pos = _reading_extracted_text.find(choice_text)
                return pos if pos >= 0 else float('inf')
            
            sorted_choices = sorted(choices, key=get_position_in_text)
            print(f"  [Reading] 全文中の出現順にソート: {sorted_choices}")
            
            # 「閉じる」ボタンでダイアログを閉じる
            try:
                close_btns = driver.find_elements(By.XPATH, "//button[.//span[text()='閉じる']]")
                if close_btns:
                    driver.execute_script("arguments[0].click();", close_btns[0])
                    time.sleep(1)
            except Exception:
                pass
            
            # 各空白に対して順番に回答
            for i in range(n_blanks):
                print(f"\n  [Reading] --- 空白 {i+1}/{n_blanks} ---")
                
                if i >= len(sorted_choices):
                    print(f"  ✗ [Reading] 空白 {i+1} に対応する選択肢がありません")
                    continue
                
                target_answer = sorted_choices[i]
                print(f"  [Reading] 目標回答: {target_answer}")
                
                # 穴埋め箇所を再取得（DOMが更新される可能性があるため）
                insertion_spans = driver.find_elements(
                    By.CSS_SELECTOR, 'span[class*="InsertionQuestionBuilder__insertionPosition"]'
                )
                
                if i >= len(insertion_spans):
                    print(f"  ✗ [Reading] 空白 {i+1} の要素が見つかりません")
                    continue
                
                # 空白をJavaScriptでクリック → ダイアログ表示
                driver.execute_script("arguments[0].click();", insertion_spans[i])
                time.sleep(2)
                
                # ダイアログ内の選択肢から目標回答を探してクリック
                current_choices = driver.find_elements(
                    By.CSS_SELECTOR, 'span[class*="InsertionQuestionBuilder__insertChoice"]'
                )
                
                print(f"  [Reading] ダイアログ内の選択肢数: {len(current_choices)}")
                
                clicked = False
                for choice_elem in current_choices:
                    choice_text = choice_elem.text.strip()
                    if choice_text == target_answer:
                        ActionChains(driver).move_to_element(choice_elem).pause(0.3).click().perform()
                        print(f"  ✓ [Reading] 「{target_answer}」を選択しました")
                        clicked = True
                        time.sleep(1)
                        break
                
                if not clicked:
                    # 部分一致でも試行
                    for choice_elem in current_choices:
                        choice_text = choice_elem.text.strip()
                        if choice_text and (target_answer in choice_text or choice_text in target_answer):
                            ActionChains(driver).move_to_element(choice_elem).pause(0.3).click().perform()
                            print(f"  ✓ [Reading] 「{choice_text}」を部分一致で選択しました")
                            clicked = True
                            time.sleep(1)
                            break
                
                if not clicked:
                    print(f"  ✗ [Reading] 「{target_answer}」に一致する選択肢が見つかりませんでした")
                    available = [c.text.strip() for c in current_choices if c.text.strip()]
                    print(f"      利用可能な選択肢: {available}")
                    # 閉じるボタンでダイアログを閉じる
                    try:
                        close_btns = driver.find_elements(By.XPATH, "//button[.//span[text()='閉じる']]")
                        if close_btns:
                            driver.execute_script("arguments[0].click();", close_btns[0])
                            time.sleep(1)
                    except Exception:
                        pass
                
                time.sleep(random.uniform(config.DELAY_MIN, config.DELAY_MAX))
            
            print(f"\n  [Reading] 穴埋め回答完了: {n_blanks} 個")
        elif n_blanks == 0:
            print("  [Reading] 穴埋め箇所が見つかりませんでした")
        else:
            print("  ✗ [Reading] 保存済みの全文テキストがありません")
        
        time.sleep(random.uniform(config.DELAY_MIN, config.DELAY_MAX))
        
        # 14. 「採点」ボタンをクリックして終了
        print("\n  [Reading] 「採点」ボタンをクリック中...")
        click_reading_confirm(driver, timeout=5)
        
    # 全て完了後に元のURLに戻る
    driver.get(url)
    
    return Isinsert
