# main.py

import os
import re
import time
import random
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException

################################################################################################################################

def quit(driver):
    if driver.session_id:
        driver.quit()
        print("Driver has been quit.")
    # while True:
    #     choice = input ("Do you want to quit the driver? (yes/no): ").strip().lower()
    #     if choice == "yes" or choice == "y":
    #         if driver.session_id:
    #             driver.quit()
    #             print("Driver has been quit.")
    #         else:
    #             print("Error: Driver is crashed by some reason.")
    #         break
    #     elif choice == "no" or choice == "n":
    #         if driver.session_id:
    #             print("Driver will keep running.")
    #         else:
    #             print("Error: Driver is crashed by some reason.")
    #         break
    #     else:
    #         print("Invalid input. Please enter \"yes (y)\" or \"no (n)\".")

################################################################################################################################

def login (driver, username, password):
    """
    Perform login to the xReading platform using provided credentials.
    
    :driver: Selenium WebDriver instance
    :username: Username for xReading
    :password: Password for xReading
    """
    web_username = driver.find_element(By.ID, "username")
    web_password = driver.find_element(By.ID, "password")

    web_username.send_keys(username)
    web_password.send_keys(password)

    login_button = driver.find_element(By.XPATH, '//button[@type="submit"]')
    login_button.click()

################################################################################################################################

def remover(text):
    lines = text.splitlines()
    filtered_lines = [line for line in lines if line.strip() != '']
    return '\n'.join(filtered_lines)



def autoread(driver, url):
    """
    Main function to execute the xReading automation tasks.
    This function should contain the logic for navigating and interacting with the xReading platform.
    """
    driver.implicitly_wait(10)
    cid_match = re.search(r'cid=(\d+)', url)
    if cid_match:
        print(f"Found: cid={cid_match.group(1)}")
        cid = f"cid={cid_match.group(1)}"
    else:
        print("Error: Could not find cid.")
        cid = f"cid=unknown"
    
    output = f"./script_{cid}.txt"
    print(output)
    if os.path.isfile(output):
        return print(f"Reading is already done for {cid}.")
    
    print(f"Starting reading for {cid}...")

    try:
        driver.get(url)
    except Exception as e:
        print("URL is not found.")
        return Exception (f"Error: {url} is not found, {e}")
    
    time.sleep(1)

    driver.execute_script("document.documentElement.style.zoom='67%'")

    with open(output, "w", encoding="utf-8") as f:
        pass

    page_num = 1

    try:
        while True:
        
            start_time = time.time()
            elapsed = 0

            print(f"Starting page {page_num}...")      

            if page_num < 5:  # 本の表紙
                next_wait = random.randint(10, 20)
            else:
                next_wait = random.randint(120, 135) # ページをめくる秒数です。　早すぎるとFail扱いになります(n敗)
            # print(f"Next page will be loaded in {next_wait} seconds.")

            time.sleep(3)

            html = driver.page_source

            soup = BeautifulSoup(html, 'html.parser')

            content_div = soup.select_one('.ajax-content.reader-book-title')

            extracted = content_div.get_text(separator='\n').strip()

            text = remover(extracted)

            with open(output, "a", encoding="utf-8") as f:
                f.write(f"\n\n===== Page {page_num} =====\n\n")
                f.write(text)
            print(f"page {page_num} is saved to {output}.")

            while elapsed < next_wait:
                if page_num < 5:
                    scroll_wait = random.randint(10, 15)    
                else:
                    scroll_wait = random.randint(15, 25)
                time.sleep(scroll_wait)

                scroll_y = random.randint(768, 876) # Scroll amount
                driver.execute_script(f"window.scrollBy(0, {scroll_y});")

                elapsed = time.time() - start_time
                print(f" ⏳ {int(elapsed)} sec elapsed, scrolling...")

            time.sleep(5)

            buttons = driver.find_elements(By.XPATH, '//button[contains(text(), "Next") or contains(text(), "次へ")]')

            if buttons and buttons[0].is_displayed() and buttons[0].is_enabled():
                print("Going to next page...")
                buttons[0].click()
                page_num += 1
            else:
                print(f"Readings are successfully completed for {cid}.")
                driver.get("https://www.xreading.com/blocks/institution/dashboard.php")
                break

    except Exception as e:
        os.remove(output)
        print(f"Error while reading: cid={cid}, page={page_num} {e}")
        driver.get("https://www.xreading.com/blocks/institution/dashboard.php")
        return Exception(f"Error: {e}")