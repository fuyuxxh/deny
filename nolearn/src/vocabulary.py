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

def _get_translation(word: str) -> str:
    url = "https://translate.googleapis.com/translate_a/single?client=gtx&sl=en&tl=ja&dt=t&q=" + urllib.parse.quote(word)
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode('utf-8'))
            return data[0][0][0]
    except Exception as e:
        print(f"  [Vocabulary] 翻訳エラー: {e}")
        return ""

def _calc_score(translated: str, choice: str) -> float:
    translated = translated.strip()
    choice = choice.strip()
    if not translated or not choice:
        return 0.0
    if translated == choice:
        return 1.0
    if translated in choice or choice in translated:
        return 0.8
    return difflib.SequenceMatcher(None, translated, choice).ratio()

def solve_vocabulary_question(driver, timeout: int = 10) -> bool:
    """
    出題された英単語の意味を選択肢から選んでクリックする。
    """
    print("\n  [Vocabulary] 問題を解析中...")
    
    # 1. 問題の英単語を取得
    question_selector = 'div.MultipleChoiceQuestionBuilder__question___3Xy0n'
    try:
        q_elem = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, question_selector))
        )
        eng_word = q_elem.text.strip()
        print(f"  [Vocabulary] 問題: {eng_word}")
    except Exception as e:
        print(f"  ✗ [Vocabulary] 問題の英単語が見つかりませんでした。")
        return False
        
    # 2. 翻訳
    translated_jp = _get_translation(eng_word)
    print(f"  [Vocabulary] Google翻訳: {translated_jp}")
    
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
        
    # 4. 一番近い選択肢を選ぶ
    best_btn = choices[0][0]
    best_score = -1.0
    best_idx = 1
    
    for idx, (btn, text) in enumerate(choices, 1):
        score = _calc_score(translated_jp, text)
        if score > best_score:
            best_score = score
            best_btn = btn
            best_idx = idx
            
    # 5. クリック
    try:
        print(f"  ✓ [Vocabulary] 選択肢 {best_idx} をクリックします (スコア: {best_score:.2f})")
        delay = random.uniform(2.5, 7.5)
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
    # --- step1 を 1回実行 ---
    print("\n  [System] まず step1 を実行します (なければスキップ)。")
    start_vocabulary_learning(driver, target_step="btn-step1", timeout=5)
    
    # 1問目があるか確認して解く
    if solve_vocabulary_question(driver, timeout=5):
        # 2問目以降を解き続ける
        while solve_vocabulary_question(driver, timeout=5):
            pass
        time.sleep(2)
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
        time.sleep(2)
        
        # 次のループのためにメニューに戻る
        driver.get(url)

    # すべて終了したら元のURLに戻って終了
    print(f"  [System] すべての処理が完了しました。{url} に戻って終了します。")
    driver.get(url)