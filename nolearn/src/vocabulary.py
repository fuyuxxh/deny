"""
単語学習 (vocabulary) に関連する自動化機能
"""
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import urllib.request
import urllib.parse
import json
import difflib
import time
import random
import src.config as config

def start_vocabulary_learning(driver, target_step: str, timeout: int = 10) -> bool:
    """
    一連の「学習する」ボタン等をクリックして学習を開始する。
    """
    print(f"\n  [Vocabulary] 学習開始シーケンス({target_step})を実行します...")
    
    # 1. 最初の「学習する」ボタン (stmenu) - 存在する場合のみクリック
    selector_menu = 'a[href^="/student/dictan-r/stmenu/"].btn_tango'
    try:
        elem_menu = WebDriverWait(driver, 3).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, selector_menu))
        )
        elem_menu.click()
        print("  ✓ [Vocabulary] 「stmenu」ボタンをクリックしました")
    except Exception:
        pass

    # 2. 次の「学習する」ボタン (ststart, id="link_drill_sl_en")
    selector_start = 'a#link_drill_sl_en'
    try:
        elem_start = WebDriverWait(driver, timeout).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, selector_start))
        )
        elem_start.click()
        print("  ✓ [Vocabulary] 「link_drill_sl_en」ボタンをクリックしました")
    except Exception as e:
        print(f"  ✗ [Vocabulary] #link_drill_sl_en が見つかりませんでした。")
        return False

    # 3. 指定された step ボタン (id=target_step)
    selector_step = f'div#{target_step}'
    try:
        elem_step = WebDriverWait(driver, timeout).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, selector_step))
        )
        elem_step.click()
        print(f"  ✓ [Vocabulary] 「{target_step}」ボタンをクリックしました")
        
        # 遷移中を待機
        try:
            WebDriverWait(driver, timeout).until(EC.staleness_of(elem_step))
            print("  ✓ [Vocabulary] 画面遷移を完了しました")
        except Exception:
            pass
            
        return True
    except Exception as e:
        print(f"  ✗ [Vocabulary] {target_step} ボタンが見つからないか、クリック不可です。")
        return False

def _get_translation(word: str, sl: str = "en", tl: str = "ja") -> list[str]:
    """
    Google翻訳で翻訳する。dt=at(代替翻訳)+dt=bd(辞書)も取得して類義語リストとして返す。
    戻り値: 翻訳結果のリスト（メイン翻訳 + 代替翻訳 + 辞書エントリ）。空リストの場合は翻訳失敗。
    """
    url = f"https://translate.googleapis.com/translate_a/single?client=gtx&sl={sl}&tl={tl}&dt=t&dt=at&dt=bd&q=" + urllib.parse.quote(word)
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode('utf-8'))
            results = []
            # メイン翻訳 (data[0][0][0])
            if data and data[0] and data[0][0]:
                main_translation = data[0][0][0]
                if main_translation:
                    results.append(main_translation)
            # 代替翻訳 (data[5][0][2] に [[alt1, ...], [alt2, ...], ...] の形式)
            try:
                if data and len(data) > 5 and data[5]:
                    for entry in data[5]:
                        if entry and len(entry) > 2 and entry[2]:
                            for alt in entry[2]:
                                if alt and alt[0] and alt[0] not in results:
                                    results.append(alt[0])
            except (IndexError, TypeError):
                pass
            # 辞書エントリ (data[1] に [[品詞, [翻訳1, 翻訳2, ...], ...], ...] の形式)
            try:
                if data and len(data) > 1 and data[1]:
                    for pos_entry in data[1]:
                        if pos_entry and len(pos_entry) > 1 and pos_entry[1]:
                            for dict_word in pos_entry[1]:
                                if dict_word and dict_word not in results:
                                    results.append(dict_word)
            except (IndexError, TypeError):
                pass
            return results
    except Exception as e:
        print(f"  [Vocabulary] 翻訳エラー: {e}")
        return []

def _calc_single_score(a: str, b: str) -> float:
    """2つの文字列間の類似度スコアを計算する。"""
    a = a.strip().lower()
    b = b.strip().lower()
    if not a or not b:
        return 0.0
    if a == b:
        return 1.0
    if a in b or b in a:
        return 0.8
    return difflib.SequenceMatcher(None, a, b).ratio()

def _calc_score(translated_list: list[str], choice: str) -> float:
    """
    翻訳結果リストと選択肢テキストを比較し、最高スコアを返す。
    """
    if not translated_list or not choice:
        return 0.0
    return max(_calc_single_score(t, choice) for t in translated_list)

_question_attempts = {}

def solve_vocabulary_question(driver, timeout: int = 10) -> bool:
    """
    出題された英単語の意味を選択肢から選んでクリックする。
    """
    global _question_attempts
    print("\n  [Vocabulary] 問題を解析中...")
    
    import re
    # 1. 問題の単語を取得
    question_selector = 'div.MultipleChoiceQuestionBuilder__question___3Xy0n'
    try:
        q_elem = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, question_selector))
        )
        question_word = q_elem.text.strip()
        print(f"  [Vocabulary] 問題: {question_word}")
    except Exception as e:
        print(f"  ✗ [Vocabulary] 問題の単語が見つかりませんでした。")
        return False
        
    # 2. 翻訳（代替翻訳リスト付き）
    # 問題が日本語か英語か判定 (ひらがな、カタカナ、漢字を含むか)
    is_ja = bool(re.search(r'[\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FFF]', question_word))
    if is_ja:
        translated_list = _get_translation(question_word, sl="ja", tl="en")
        reverse_sl, reverse_tl = "en", "ja"
        print(f"  [Vocabulary] Google翻訳(ja->en): {translated_list}")
    else:
        translated_list = _get_translation(question_word, sl="en", tl="ja")
        reverse_sl, reverse_tl = "ja", "en"
        print(f"  [Vocabulary] Google翻訳(en->ja): {translated_list}")
    
    # 3. 選択肢を取得
    choices = []
    base_xpath = '//*[@id="root"]/div/div/div[2]/div/div/div[3]/div/div/div[3]/ul/li[{}]/div/button'
    
    try:
        for i in range(1, 5):
            xpath = base_xpath.format(i)
            btn = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.XPATH, xpath))
            )
            text = btn.text.strip()
            choices.append((btn, text))
            print(f"  [Vocabulary] 選択肢 {i}: {text}")
    except Exception as e:
        print(f"  ✗ [Vocabulary] 選択肢の取得に失敗しました。")
        return False
        
    if not choices:
        return False
        
    # 4. 一番近い選択肢を選ぶ（過去に間違えたものを除外）
    tried_choices = _question_attempts.get(question_word, set())
    valid_choices = []
    
    for idx, (btn, text) in enumerate(choices, 1):
        if text in tried_choices:
            print(f"    - 選択肢 '{text}' は過去に失敗したため除外します。")
        else:
            valid_choices.append((idx, btn, text))
            
    # 全ての選択肢を除外してしまった場合のフェールセーフ
    if not valid_choices:
        print("  [System] すべての選択肢を試しました。この問題の履歴をリセットします。")
        _question_attempts[question_word] = set()
        valid_choices = [(idx, btn, text) for idx, (btn, text) in enumerate(choices, 1)]

    best_btn = valid_choices[0][1]
    best_text = valid_choices[0][2]
    best_score = -1.0
    best_idx = valid_choices[0][0]
    
    for idx, btn, text in valid_choices:
        # 順方向スコア: 翻訳リスト vs 選択肢（全体）
        forward_score = _calc_score(translated_list, text)
        
        # 順方向スコア（パーツ別）: 選択肢を「、」で分割して各パーツとも比較
        parts = [p.strip() for p in text.split('、') if p.strip()]
        if len(parts) > 1:
            for part in parts:
                part_score = _calc_score(translated_list, part)
                if part_score > forward_score:
                    forward_score = part_score
        
        # 逆方向スコア: 選択肢を逆翻訳して問題文と比較
        reverse_score = 0.0
        try:
            # 全体を逆翻訳
            reverse_translations = _get_translation(text, sl=reverse_sl, tl=reverse_tl)
            if reverse_translations:
                reverse_score = max(
                    _calc_single_score(rt, question_word) for rt in reverse_translations
                )
            
            # パーツ別に逆翻訳（「、」区切りの複合フレーズ対応）
            if len(parts) > 1:
                for part in parts:
                    part_translations = _get_translation(part, sl=reverse_sl, tl=reverse_tl)
                    if part_translations:
                        part_reverse = max(
                            _calc_single_score(rt, question_word) for rt in part_translations
                        )
                        if part_reverse > reverse_score:
                            reverse_score = part_reverse
            
            if reverse_score > 0.5:
                print(f"    + 選択肢 '{text}' の逆翻訳が問題文と一致 (スコア: {reverse_score:.2f})")
        except Exception:
            pass
        
        # 最終スコア: 順方向と逆方向の最大値を採用
        score = max(forward_score, reverse_score)
        if score > best_score:
            best_score = score
            best_btn = btn
            best_text = text
            best_idx = idx

    # 今回試す選択肢を履歴に記録
    _question_attempts.setdefault(question_word, set()).add(best_text)
            
    # 5. クリック
    try:
        print(f"  ✓ [Vocabulary] 選択肢 {best_idx} をクリックします (スコア: {best_score:.2f})")
        delay = random.uniform(config.DELAY_MIN, config.DELAY_MAX)
        print(f"  [System] ボット検知回避のため {delay:.1f} 秒待機します...")
        time.sleep(delay)
        best_btn.click()
        
        # クリック後、選択肢ボタンが画面から消える（＝次の問題に更新される）のを待機
        try:
            WebDriverWait(driver, 3).until(EC.staleness_of(best_btn))
        except Exception:
            pass
            
        return True
    except Exception as e:
        print(f"  ✗ [Vocabulary] ボタンのクリックに失敗しました: {e}")
        return False

def run_vocabulary_automation(driver, url: str):
    """
    英単語学習（step1を1回実行後、step2を無限ループ）を自動化する。
    """
    global _question_attempts
    _question_attempts.clear()

    # --- step1 を 1回実行 ---
    print("\n  [System] まず step1 を実行します (なければスキップ)。")
    start_vocabulary_learning(driver, target_step="btn-step1", timeout=5)
    
    # 1問目があるか確認して解く
    if solve_vocabulary_question(driver, timeout=5):
        # 2問目以降を解き続ける
        while solve_vocabulary_question(driver, timeout=5):
            pass
        delay = random.uniform(config.DELAY_MIN, config.DELAY_MAX)
        time.sleep(delay)
    else:
        print("  [System] step1 の問題が取得できませんでした（完了済み等）。スキップします。")
        
    # step1完了後、あるいはスキップした場合でも、メニュー状態をリセットする
    driver.get(url)

    # --- step2 を無限ループ ---
    print("\n  [System] 続いて step2 の無限ループに入ります。")
    while True:
        started = start_vocabulary_learning(driver, target_step="btn-step2", timeout=5)
        if not started:
            print(f"\n  [System] step2 のボタンが見つかりません。ループを終了します。")
            break
        
        # 1問目があるか確認して解く
        first_q_solved = solve_vocabulary_question(driver, timeout=5)
        if not first_q_solved:
            print(f"\n  [System] step2 の問題が取得できませんでした（完了済み等）。ループを終了します。")
            break
        
        # 2問目以降を解き続ける
        while solve_vocabulary_question(driver, timeout=5):
            pass
        delay = random.uniform(config.DELAY_MIN, config.DELAY_MAX)
        time.sleep(delay)
        
        # 次のループのためにメニューに戻る
        driver.get(url)

    # すべて終了したら元のURLに戻って終了
    print(f"  [System] すべての処理が完了しました。{url} に戻って終了します。")
    driver.get(url)
    