import atexit
from os import path, makedirs
from queue import Queue
import traceback
import pandas as pd
from crawlers import CrawlerGoogleNews
import requests


INPUT_CSV = './datas/inputs/task1.csv'
DEBUG_DIR = './debug_html/task1'
OUTPUT_DIR = './datas/outputs/task1'

makedirs(DEBUG_DIR, exist_ok=True)
makedirs(OUTPUT_DIR, exist_ok=True)


USE_VPN = True
IDLE_SEC = 3
RESULT_PER_PAGE = 200

TARGET_LANG = 'en'
MAX_SEARCH = 200

VERBOSE = True

def display_inital():
    print(f"""
[Start Crawling - Task1]

1. Direcory Settings
INPUT_CSV       = {INPUT_CSV}
DEBUG_DIR       = {DEBUG_DIR}
OUTPUT_DIR      = {OUTPUT_DIR}

2. Crawler Settings
USE_VPN         = {USE_VPN}
IDLE_SEC        = {IDLE_SEC}
RESULT_PER_PAGE = {RESULT_PER_PAGE}

3. Search Setting
TARGET_LANG = {TARGET_LANG}
MAX_SEARCH  = {MAX_SEARCH}
""")

def get_keywords():
    inputs = pd.read_csv(INPUT_CSV)
    return  list(inputs.keyword.values)

def init_crawler():
    return CrawlerGoogleNews(
        # test_url        = '',
        result_per_page = RESULT_PER_PAGE,
        use_vpn         = USE_VPN,
        idle_sec        = IDLE_SEC,
        debug_dir       = DEBUG_DIR,
        verbose         = VERBOSE
    )

def conv_file_csv(keyword):
    file_csv = keyword.replace(' ','_').replace('\"','')
    return f"{file_csv}.csv"


def run_task(crawler, keyword, path_csv, remain):

    print(f"[{remain}] Start single search task: {keyword}")

    # Run Task
    news_urls = crawler.run(
        keyword=keyword,
        lang=TARGET_LANG,
        max_search=MAX_SEARCH
    )

    # Save Task results
    if news_urls:
        pd.DataFrame(dict(
            keyword = [keyword] * len(news_urls),
            urls = news_urls,
        )).to_csv(path_csv, index=False, encoding='utf-8-sig')
        print(f"[{remain}] Complete single search task: {keyword}")
    else:
        pd.DataFrame(dict(
            keyword = [keyword],
            urls    = ['No search results'],
        )).to_csv(
            path_csv.replace('.csv', '_no_search_result.csv'),
            index=False, encoding='utf-8-sig'
        )
        print(f"[{remain}] No search results: {keyword}")

def terminate_vpn_gate(crawler):
    if crawler.use_vpn:
        crawler.vpn_gate.disconnect()
    del crawler


if __name__ == '__main__':

    display_inital()
    keywords = get_keywords()
    crawler = init_crawler()
    atexit.register(terminate_vpn_gate, crawler=crawler)

    q_keyword = Queue()
    for i, keyword in enumerate(keywords):
        file_csv = conv_file_csv(keyword)
        path_csv = path.join(OUTPUT_DIR, file_csv)
        if path.isfile(path_csv) or path.isfile(path_csv.replace('.csv', '_no_search_result.csv')):
            continue
        q_keyword.put((keyword, path_csv,))


    print(f"Total task: {q_keyword.qsize()}")
    while not q_keyword.empty():
        try:
            keyword, path_csv = q_keyword.get_nowait()
            run_task(crawler, keyword, path_csv, remain=q_keyword.qsize())

        except requests.exceptions.ConnectionError as e:
            if crawler.use_vpn:
                crawler.vpn_gate.connect_server()
                q_keyword.put((keyword, path_csv,))
            else:
                print("Fatal Error - {e}")
                break

        except Exception as e:
            print(e)
            print(traceback.format_exc())
            if crawler.use_vpn:
                crawler.vpn_gate.disconnect()
            del crawler
            crawler = init_crawler()
            q_keyword.put((keyword, path_csv,))