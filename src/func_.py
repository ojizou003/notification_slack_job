from time import sleep
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from tqdm.auto import tqdm
import pickle
import requests
import json
from dotenv import load_dotenv, find_dotenv
import os


def get_title(KEYWORD: str):
    """
    引数に検索するキーワードを入力
    戻り値は、クラウドワークス、ランサーズ、ココナラそれぞれの検索結果先頭のタイトル
    """
    CW_URL = "https://crowdworks.jp/public/jobs?ref=login_header"
    RC_URL = "https://www.lancers.jp/work/search?open=1&ref=header_menu"
    CC_URL = "https://coconala.com/requests?recruiting=true"

    driver_path = ChromeDriverManager().install()
    options = Options()
    options.add_argument("--headless")
    service = Service(executable_path=driver_path)
    browser = webdriver.Chrome(options=options, service=service)
    browser.maximize_window()

    # Ｘ クラウドワークスの先頭のタイトルを取得
    # 〇 クラウドワークスは新着が必ずしも先頭にこないのでul全体の文字列を取得
    browser.get(CW_URL)
    body = WebDriverWait(browser, 15).until(
        EC.presence_of_all_elements_located((By.TAG_NAME, "body"))
    )
    browser.implicitly_wait(5)
    browser.find_element(By.CSS_SELECTOR, 'input._o6He').click()
    browser.find_element(By.NAME, "search[keywords]").send_keys(KEYWORD)
    browser.find_element(By.CSS_SELECTOR, "button.HuexB").click()
    body = WebDriverWait(browser, 15).until(
        EC.presence_of_all_elements_located((By.TAG_NAME, "body"))
    )
    CW_URL_R = browser.current_url
    with open('../data/cw_url_r.pkl', 'wb') as f: 
        pickle.dump(CW_URL_R, f)
    html = browser.page_source
    soup = BeautifulSoup(html, "lxml")
    cw_new = soup.find('ul', class_='gH9lt OW4Y6 QH0Pz').find('a').text

    # ランサーズの先頭のタイトルを取得
    browser.get(RC_URL)
    body = WebDriverWait(browser, 15).until(
        EC.presence_of_all_elements_located((By.TAG_NAME, "body"))
    )
    browser.find_element(By.ID, "Keyword").send_keys(KEYWORD)
    browser.find_element(By.CSS_SELECTOR, "button#Search").click()
    body = WebDriverWait(browser, 15).until(
        EC.presence_of_all_elements_located((By.TAG_NAME, "body"))
    )
    RC_URL_R = browser.current_url
    with open('../data/rc_url_r.pkl', 'wb') as f: 
        pickle.dump(RC_URL_R, f)
    html = browser.page_source
    soup = BeautifulSoup(html, "lxml")
    rc_new = (
        soup.find("a", class_="p-search-job-media__title c-media__title")
        .text.replace("\n", "")
        .replace("NEW", "")
        .strip()
    )

    # ココナラの先頭のタイトルを取得
    browser.get(CC_URL)
    body = WebDriverWait(browser, 15).until(
        EC.presence_of_all_elements_located((By.TAG_NAME, "body"))
    )
    browser.find_element(By.TAG_NAME, "input").send_keys(KEYWORD)
    browser.find_element(
        By.CSS_SELECTOR, "button.button.d-searchInput_searchButton"
    ).click()
    body = WebDriverWait(browser, 15).until(
        EC.presence_of_all_elements_located((By.TAG_NAME, "body"))
    )
    CC_URL_R = browser.current_url
    with open('../data/cc_url_r.pkl', 'wb') as f: 
        pickle.dump(CC_URL_R, f)
    html = browser.page_source
    soup = BeautifulSoup(html, "lxml")
    cc_new = soup.find("div", class_="c-itemInfo_title").text.replace("\n", "").strip()

    browser.quit()

    return cw_new, rc_new, cc_new


def notify_newjob(cw_new, rc_new, cc_new):
    """
    引数にクラウドワークス、ランサーズ、ココナラそれぞれの検索結果先頭のタイトルとWEB_HOOK_URLを入れ、
    検索結果が前回と変わっていたら、スラックで通知する
    戻り値なし
    """
    # 前回のタイトルを復元
    with open("../data/cw.pkl", "rb") as f:
        cw = pickle.load(f)
    with open("../data/rc.pkl", "rb") as f:
        rc = pickle.load(f)
    with open("../data/cc.pkl", "rb") as f:
        cc = pickle.load(f)

    # slackの送信に使うWEB_HOOK_URLを取得
    load_dotenv(find_dotenv())
    WEB_HOOK_URL = os.getenv('WEB_HOOK_URL')

    # クラウドワークスに新しい仕事があった場合、スラックにメッセージを送り、cw.pklを更新する
    if cw != cw_new:
        with open('../data/cw_url_r.pkl', 'rb') as f:
            CW_URL_R = pickle.load(f)
        message = f"クラウドワークスに新しい仕事があります\n{CW_URL_R}"
        payload = {"text": message}
        requests.post(WEB_HOOK_URL, json=payload)
        cw = cw_new
        with open("../data/cw.pkl", "wb") as f:
            pickle.dump(cw, f)
    else:
        pass
    sleep(1)

    # ランサーズに新しい仕事があった場合、スラックにメッセージを送り、rc.pklを更新する
    if rc != rc_new:
        with open('../data/rc_url_r.pkl', 'rb') as f:
            RC_URL_R = pickle.load(f)
        message = f"ランサーズに新しい仕事があります\n{rc_new}\n{RC_URL_R}"
        payload = {"text": message}
        requests.post(WEB_HOOK_URL, json=payload)
        rc = rc_new
        with open("../data/rc.pkl", "wb") as f:
            pickle.dump(rc, f)
    else:
        pass
    sleep(1)

    # ココナラに新しい仕事があった場合、スラックにメッセージを送り、cc.pklを更新する
    if cc != cc_new:
        with open('../data/cc_url_r.pkl', 'rb') as f:
            CC_URL_R = pickle.load(f)
        message = f"ココナラに新しい仕事があります\n{cc_new}\n{CC_URL_R}"
        payload = {"text": message}
        requests.post(WEB_HOOK_URL, json=payload)
        cc = cc_new
        with open("../data/cc.pkl", "wb") as f:
            pickle.dump(cc, f)
    else:
        pass
    sleep(1)
