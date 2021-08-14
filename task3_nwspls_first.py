#%%
import atexit
from os import path, makedirs, listdir
from queue import Queue
import traceback
import pandas as pd
from crawlers import CrawlerNewsPlease
import requests


INPUT_DIR = './datas/outputs/task1'
DEBUG_DIR = './debug_html/task3'
OUTPUT_DIR = './datas/outputs/task3'

makedirs(DEBUG_DIR, exist_ok=True)
makedirs(OUTPUT_DIR, exist_ok=True)


USE_VPN = True
IDLE_SEC = 3
VERBOSE = True

def display_inital():
    print(f"""
[Start Crawling - Task3]

1. Direcory Settings
DEBUG_DIR       = {DEBUG_DIR}
OUTPUT_DIR      = {OUTPUT_DIR}

2. Crawler Settings
USE_VPN         = {USE_VPN}
IDLE_SEC        = {IDLE_SEC}

""")

def load_inputs():
    return pd.concat([
        pd.read_csv(path.join(INPUT_DIR, file_csv))
        for file_csv in listdir(INPUT_DIR)
        if file_csv.endswith('.csv')
    ]).values

inputs = load_inputs()

#%%
def init_crawler():
    return CrawlerNewsPlease(
        use_vpn         = USE_VPN,
        idle_sec        = IDLE_SEC,
        debug_dir       = DEBUG_DIR,
        verbose         = VERBOSE
    )



def terminate_vpn_gate(crawler):
    if crawler.use_vpn:
        crawler.vpn_gate.disconnect()
    del crawler

def pack_result(keyword, url, article):

    if article != None:
        return dict(
            keyword       = keyword,
            source_domain = article.source_domain,
            date_publish  = article.date_publish,
            language      = article.language,
            title         = article.title,
            maintext      = article.maintext,
            url           = url,
        )
    else:
        return dict(
            keyword       = [keyword],
            source_domain = ['No search result'],
            date_publish  = ['No search result'],
            language      = ['No search result'],
            title         = ['No search result'],
            maintext      = ['No search result'],
            url           = ['No search result'],
        )

if __name__ == '__main__':

    display_inital()
    inputs = load_inputs()
    crawler = init_crawler()
    atexit.register(terminate_vpn_gate, crawler=crawler)

    q_keyword = Queue()
    for i, (keyword, url,) in enumerate(inputs):
        q_keyword.put((keyword, url,) )


    total_n = q_keyword.qsize()
    results = []
    print(f"Total task: {q_keyword.qsize()}")
    while not q_keyword.empty():
        print(f"[{len(results)}/{total_n}]")
        try:

            keyword, url = q_keyword.get_nowait()
            if url == 'No search results':
                results.append(pack_result(keyword, url, article=None))
            else:
                article = crawler.run(url)
                results.append(pack_result(keyword, url, article))
        except requests.exceptions.ConnectionError as e:
            if crawler.use_vpn:
                crawler.vpn_gate.connect_server()
                q_keyword.put((keyword, url,))
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
            q_keyword.put((keyword, url,))

    pd.DataFrame(results).to_csv(path.join(OUTPUT_DIR, "task3_res.csv"))