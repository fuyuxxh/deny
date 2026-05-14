from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import urllib.request
import urllib.parse
import json
import time
import random
import src.config as config

def start_grammar_learning(driver, target_step: str, timeout: int = 10) -> bool:
    """
    Grammarの学習開始ボタンと対象のstepボタンをクリックする。
    """
    print(f"\n  [Grammar] 学習開始シーケンス({target_step})を実行します...")
    
    # 1. Grammarの「学習する」ボタン
    selector_start = 'a[href^="/student/sorting/ststart/grammar/"].btn_grammar'
    try:
        elem_start = WebDriverWait(driver, 3).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, selector_start))
        )
        elem_start.click()
        print("  ✓ [Grammar] 「学習する (grammar)」ボタンをクリックしました")
    except Exception:
        pass # すでに遷移済みでボタンがない場合は無視

    # 2. 指定された step ボタン (id=target_step)
    selector_step = f'div#{target_step}'
    try:
        elem_step = WebDriverWait(driver, timeout).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, selector_step))
        )
        elem_step.click()
        print(f"  ✓ [Grammar] 「{target_step}」ボタンをクリックしました")
        
        # 遷移中を待機
        try:
            WebDriverWait(driver, timeout).until(EC.staleness_of(elem_step))
            print("  ✓ [Grammar] 画面遷移を完了しました")
        except Exception:
            pass
            
        return True
    except Exception as e:
        print(f"  ✗ [Grammar] {target_step} ボタンが見つからないか、クリック不可です。")
        return False

import re

def _get_best_grammar_choice(sentence: str, choices: list) -> int:
    """
    Google Ngram APIを使用して、文脈（前後の単語）に最も合致する選択肢のインデックス(0〜3)を返す。
    名詞や形容詞など、翻訳では判別できない品詞の違いをコーパスの出現頻度で正確に判定する。
    """
    if "-------" not in sentence:
        return 0

    left, right = sentence.split("-------", 1)
    
    # 記号を取り除いて小文字化し、単語リストを作成
    left_words = [re.sub(r'[^a-z0-9]', '', w.lower()) for w in left.split()]
    right_words = [re.sub(r'[^a-z0-9]', '', w.lower()) for w in right.split()]
    left_words = [w for w in left_words if w]
    right_words = [w for w in right_words if w]
    
    w_prev = left_words[-1] if left_words else ""
    w_next = right_words[0] if right_words else ""
    
    queries = []
    query_to_info = {} # query_string -> (choice_idx, ngram_type)
    
    for i, choice in enumerate(choices):
        c = re.sub(r'[^a-z0-9]', '', choice.lower())
        if not c:
            continue
            
        # 3-gram: w_prev + choice + w_next
        if w_prev and w_next:
            q3 = f"{w_prev} {c} {w_next}"
            queries.append(q3)
            query_to_info[q3] = (i, 3)
            
        # 2-gram (Left): w_prev + choice
        if w_prev:
            q2l = f"{w_prev} {c}"
            queries.append(q2l)
            query_to_info[q2l] = (i, 2)
            
        # 2-gram (Right): choice + w_next
        if w_next:
            q2r = f"{c} {w_next}"
            queries.append(q2r)
            query_to_info[q2r] = (i, 2)

    if not queries:
        return 0
        
    unique_queries = list(set(queries))
    results = {}
    
    # Ngram APIはカンマ区切りで複数クエリ可能（最大12程度推奨）
    chunk_size = 12
    for i in range(0, len(unique_queries), chunk_size):
        chunk = unique_queries[i:i+chunk_size]
        chunk_str = ",".join(chunk)
        # 空白は+に、カンマはそのままにする
        content = urllib.parse.quote_plus(chunk_str, safe=',')
        url = f"https://books.google.com/ngrams/json?content={content}&year_start=2000&year_end=2019&corpus=26&smoothing=3"
        req = urllib.request.Request(url)
        try:
            with urllib.request.urlopen(req) as response:
                data = json.loads(response.read().decode('utf-8'))
                for item in data:
                    ngram = item['ngram'].lower()
                    # 最後の年の頻度を取得、または平均
                    avg_freq = sum(item['timeseries']) / len(item['timeseries']) if item['timeseries'] else 0
                    results[ngram] = avg_freq
        except Exception as e:
            print(f"  [Grammar] Ngram API エラー: {e}")
            
    score_3gram = [0.0] * len(choices)
    score_2gram = [0.0] * len(choices)
    
    for q, freq in results.items():
        if q in query_to_info:
            c_idx, n_type = query_to_info[q]
            if n_type == 3:
                score_3gram[c_idx] += freq
            elif n_type == 2:
                score_2gram[c_idx] += freq
                
    for i in range(len(choices)):
        print(f"    - 選択肢 '{choices[i]}' のNgramスコア -> 3-gram: {score_3gram[i]:.2e}, 2-gram: {score_2gram[i]:.2e}")

    max_3gram = max(score_3gram)
    if max_3gram > 0:
        return score_3gram.index(max_3gram)
        
    max_2gram = max(score_2gram)
    if max_2gram > 0:
        return score_2gram.index(max_2gram)
        
    return 0

_question_attempts = {}

def solve_grammar_question(driver, timeout: int = 10) -> bool:
    """
    文法問題を解析し、{-------}の前後の文脈から最も出現頻度が高い選択肢を選ぶ。
    同じ問題で間違えた場合、過去に選んだ選択肢を除外して無限ループを防ぐ。
    """
    global _question_attempts
    
    print("\n  [Grammar] 問題を解析中...")
    
    # 1. 問題の文章を取得
    question_selector = 'div.MultipleChoiceQuestionBuilder__question___3Xy0n'
    try:
        q_elem = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, question_selector))
        )
        question_text = q_elem.text.strip()
        print(f"  [Grammar] 問題: {question_text}")
    except Exception:
        print(f"  ✗ [Grammar] 問題の文章が見つかりませんでした。")
        return False
        
    if "-------" not in question_text:
        print(f"  ✗ [Grammar] 問題文に ------- が含まれていません。")
        return False

    # 2. 選択肢を取得
    choices = []
    base_xpath = '//*[@id="root"]/div/div/div[2]/div/div/div[3]/div/div/div[3]/ul/li[{}]/div/button'
    
    try:
        for i in range(1, 5):
            xpath = base_xpath.format(i)
            btn = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.XPATH, xpath))
            )
            # span等を含めたボタン内のテキストを取得
            text = btn.text.strip()
            choices.append((btn, text))
            print(f"  [Grammar] 選択肢 {i}: {text}")
    except Exception as e:
        print(f"  ✗ [Grammar] 選択肢の取得に失敗しました。")
        return False
        
    if not choices:
        return False
        
    # 3. 最適な選択肢を評価（Ngram APIを利用）
    # 過去に間違えた選択肢は候補から除外する
    tried_choices = _question_attempts.get(question_text, set())
    valid_choices_map = []
    valid_choice_texts = []
    
    for idx, (btn, text) in enumerate(choices):
        if text in tried_choices:
            print(f"    - 選択肢 '{text}' は過去に失敗したため除外します。")
        else:
            valid_choices_map.append((idx, btn, text))
            valid_choice_texts.append(text)
            
    # 全ての選択肢を試してしまっていた場合はこの問題の履歴をリセット（フェールセーフ）
    if not valid_choices_map:
        print("  [System] すべての選択肢を試しました。この問題の履歴をリセットします。")
        _question_attempts[question_text] = set()
        valid_choices_map = [(idx, btn, text) for idx, (btn, text) in enumerate(choices)]
        valid_choice_texts = [text for idx, btn, text in valid_choices_map]

    best_relative_idx = _get_best_grammar_choice(question_text, valid_choice_texts)
    
    original_idx, best_btn, best_text = valid_choices_map[best_relative_idx]
    best_idx = original_idx + 1
    
    # 今回試す選択肢を履歴に記録
    _question_attempts.setdefault(question_text, set()).add(best_text)
            
    # 4. クリック
    try:
        print(f"  ✓ [Grammar] 選択肢 {best_idx} をクリックします")
        delay = random.uniform(config.DELAY_MIN, config.DELAY_MAX)
        print(f"  [System] ボット検知回避のため {delay:.1f} 秒待機します...")
        time.sleep(delay)
        best_btn.click()
        
        # 画面が更新されるのを待つ
        try:
            WebDriverWait(driver, 3).until(EC.staleness_of(best_btn))
        except Exception:
            pass
            
        return True
    except Exception as e:
        print(f"  ✗ [Grammar] ボタンのクリックに失敗しました: {e}")
        return False

def run_grammar_automation(driver, url: str):
    """
    Grammar学習を自動化するエントリー関数。
    """
    global _question_attempts
    _question_attempts.clear()
    
    print("\n========================================")
    print("  [System] Grammarの自動学習処理を開始します")
    print("========================================")
    
    # --- step1 を 1回実行 ---
    print("\n  [System] まず step1 を実行します (なければスキップ)。")
    start_grammar_learning(driver, target_step="btn-step1", timeout=5)
    
    if solve_grammar_question(driver, timeout=5):
        while solve_grammar_question(driver, timeout=5):
            pass
        delay = random.uniform(config.DELAY_MIN, config.DELAY_MAX)
        time.sleep(delay)
    else:
        print("  [System] step1 の問題が取得できませんでした（完了済み等）。スキップします。")
        
    driver.get(url)

    # --- step2 を無限ループ ---
    print("\n  [System] 続いて step2 の無限ループに入ります。")
    while True:
        started = start_grammar_learning(driver, target_step="btn-step2", timeout=5)
        if not started:
            print(f"\n  [System] step2 のボタンが見つかりません。ループを終了します。")
            break
        
        first_q_solved = solve_grammar_question(driver, timeout=5)
        if not first_q_solved:
            print(f"\n  [System] step2 の問題が取得できませんでした（完了済み等）。ループを終了します。")
            break
        
        while solve_grammar_question(driver, timeout=5):
            pass
        delay = random.uniform(config.DELAY_MIN, config.DELAY_MAX)
        time.sleep(delay)
        
        driver.get(url)

    print(f"  [System] Grammarの処理がすべて完了しました。{url} に戻ります。")
    driver.get(url)
