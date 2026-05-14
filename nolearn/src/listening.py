from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import random
import src.config as config

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

def type_listening_answer(driver, answer_text: str = "", timeout: int = 10) -> bool:
    """
    listan_box テキストエリアにテキストを入力する。
    answer_text が空の場合は何も入力しない（空回答用）。
    """
    if answer_text:
        print("\n  [Listening] テキストボックスに正解テキストを入力中...")
    else:
        print("\n  [Listening] テキストボックスを空のまま送信します（1回目: 正解取得用）...")
    
    try:
        textarea = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.ID, "listan_box"))
        )
        textarea.clear()
        if answer_text:
            textarea.send_keys(answer_text)
            print(f"  ✓ [Listening] テキストボックスに入力しました (文字数: {len(answer_text)})")
        else:
            print("  ✓ [Listening] テキストボックスは空のままです")
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
        delay = random.uniform(config.DELAY_MIN, config.DELAY_MAX)
        print(f"  [System] 判定結果の表示を待機中... ({delay:.1f} 秒)")
        time.sleep(delay)
        return True
    except Exception:
        print("  ✗ [Listening] 「判定」ボタンが見つかりませんでした。")
        return False

def extract_script_from_result(driver, timeout: int = 10) -> str:
    """
    判定結果画面から ScriptBox__previewParagraph のテキストを抽出する。
    <div class="ScriptBox__previewParagraph___..."> 内の全テキストを取得し、
    各 <div> の内容を改行区切りで連結して返す。
    """
    print("\n  [Listening] 結果画面から正解スクリプトを取得中...")
    
    # クラス名の前方一致で検索（ハッシュ部分が変わる可能性に対応）
    selector = 'div[class*="ScriptBox__previewParagraph"]'
    
    try:
        container = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, selector))
        )
        
        # 内部の各 <div> からテキストを取得
        inner_divs = container.find_elements(By.CSS_SELECTOR, "div")
        lines = []
        for div in inner_divs:
            text = div.text.strip()
            if text:
                lines.append(text)
        
        # 内部 <div> が無い場合はコンテナ全体のテキストを使用
        if not lines:
            full_text = container.text.strip()
            if full_text:
                lines = [full_text]
        
        if lines:
            script_text = "\n".join(lines)
            print(f"  ✓ [Listening] 正解スクリプトを取得しました:")
            for line in lines:
                print(f"      {line}")
            return script_text
        else:
            print("  ✗ [Listening] スクリプトのテキストが空でした。")
            return ""
            
    except Exception as e:
        print(f"  ✗ [Listening] 正解スクリプトの取得に失敗しました")
        print(f"      エラー: {type(e).__name__}: {e}")
        return ""

def run_listening_automation(driver, url: str):
    """
    Listening学習を自動化するエントリー関数。
    2パス方式:
      1回目: 空回答で判定 → 結果画面から正解スクリプトを取得
      2回目: 正解スクリプトを入力して判定
    """
    print("\n========================================")
    print("  [System] Listeningの自動学習処理を開始します")
    print("========================================")
    
    started = start_listening_learning(driver, timeout=5)
    
    if not started:
        print("  [Listening] 学習する対象が見つかりませんでした。")
        driver.get(url)
        return

    # resultTable 内のプレイヤーリンクをクリック
    clicked = click_listening_player(driver, timeout=5)
    if not clicked:
        print("  [Listening] プレイヤーリンクが見つかりませんでした。")
        driver.get(url)
        return

    # ===== 1回目: 空回答で判定し、正解スクリプトを取得 =====
    print("\n  ────────────────────────────────────")
    print("  [Listening] ▶ 1回目: 空回答で正解スクリプトを取得します")
    print("  ────────────────────────────────────")

    typed = type_listening_answer(driver, answer_text="", timeout=5)
    if not typed:
        driver.get(url)
        return

    judged = click_judge_button(driver, timeout=5)
    if not judged:
        driver.get(url)
        return

    # 結果画面から正解スクリプトを取得
    script_text = extract_script_from_result(driver, timeout=10)
    
    if not script_text:
        print("  [Listening] 正解スクリプトを取得できませんでした。元のURLに戻ります。")
        driver.get(url)
        return

    # ===== 元のURLに戻って2回目の試行を準備 =====
    delay = random.uniform(config.DELAY_MIN, config.DELAY_MAX)
    print(f"  [System] 元のURLに戻る前に {delay:.1f} 秒待機します...")
    time.sleep(delay)
    print(f"\n  [Listening] 元のURL に戻ります...")
    driver.get(url)
    delay2 = random.uniform(config.DELAY_MIN, config.DELAY_MAX)
    print(f"  [System] ページ読み込みを待機中... ({delay2:.1f} 秒)")
    time.sleep(delay2)

    # ===== 2回目: 正解スクリプトを入力して判定 =====
    print("\n  ────────────────────────────────────")
    print("  [Listening] ▶ 2回目: 正解スクリプトを入力して判定します")
    print("  ────────────────────────────────────")

    started2 = start_listening_learning(driver, timeout=5)
    if not started2:
        print("  [Listening] 2回目の学習開始に失敗しました。")
        driver.get(url)
        return

    clicked2 = click_listening_player(driver, timeout=5)
    if not clicked2:
        print("  [Listening] 2回目のプレイヤーリンクが見つかりませんでした。")
        driver.get(url)
        return

    typed2 = type_listening_answer(driver, answer_text=script_text, timeout=5)
    if not typed2:
        driver.get(url)
        return

    click_judge_button(driver, timeout=5)

    # 状態をリセットするために元のURLに戻る
    delay = random.uniform(config.DELAY_MIN, config.DELAY_MAX)
    print(f"  [System] 元のURLに戻る前に {delay:.1f} 秒待機します...")
    time.sleep(delay)
    driver.get(url)
