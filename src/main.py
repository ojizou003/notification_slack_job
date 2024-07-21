# クラウドワークス、ランサーズ、ココナラに新しい仕事が公開されたら、slackで通知する

## ライブラリのインポート
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

import func_

## 検索するキーワードの設定
KEYWORD = "スクレイピング"

## スクレイピングして先頭のタイトルを取得
cw_new, rc_new, cc_new = func_.get_title(KEYWORD)

## 前回のタイトルから変わっているならslackで通知
func_.notify_newjob(cw_new, rc_new, cc_new)
