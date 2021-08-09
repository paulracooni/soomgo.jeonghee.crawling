#%%
"""
[뉴스 카드 CSS 구조 분석]

1. link
#rso > div:nth-child(1) > g-card > div > div > div.dbsr

2. press
#rso > div:nth-child(1) > g-card > div > div > div.dbsr > a > div > div.hI5pFf > div.XTjFC.WF4CUc

3. title
#rso > div:nth-child(1) > g-card > div > div > div.dbsr > a > div > div.hI5pFf > div.JheGif.nDgy9d

4. summary
#rso > div:nth-child(1) > g-card > div > div > div.dbsr > a > div > div.hI5pFf > div.yJHHTd > div.Y3v8qd

5. date

#rso > div:nth-child(10) > g-card > div > div > a > div > div.iRPxbe > div.ZE0LJd.iuBdze > p > span
"""

IDLE = 2

DIR_NEWS_CRAWLING = './datas/news_crawling'


cs_root = "#rso g-card"

cs_link = "a"

cs_press = "div.XTjFC.WF4CUc"

cs_title = "div.JheGif.nDgy9d"

cs_summary = "div.Y3v8qd"

cs_date = "div.wxp1Sb > span"

cs_result_stats = "#result-stats"


import re
from os import path, makedirs, listdir
from time import sleep
from queue import Queue
import requests
from urllib.parse import quote_plus
from bs4 import BeautifulSoup

import openpyxl
import pandas as pd

from vpngate import VpnGate, saveOvpn, connect


from fake_useragent import UserAgent

def get_external_ip():
    return requests.get('https://api.ipify.org').text

def connect_vpn(try_n=2, wait_sec=10):

    current_ip = get_external_ip()
    vpn_process = __connect_vpn()
    sleep(wait_sec)

    wait_cnt = 0
    while current_ip == get_external_ip():
        if wait_cnt > try_n:
            vpn_process.terminate()
            vpn_gate = VpnGate()
            server = vpn_gate.get_server()
            path_ovpn = saveOvpn(server)
            vpn_process = connect(path_ovpn)
            wait_cnt = 0
        wait_cnt += 1
        sleep(wait_sec)

    print(f"Curent IP: {get_external_ip()}")
    return vpn_process

def __connect_vpn():
    vpn_gate = VpnGate()
    server = vpn_gate.get_server()
    path_ovpn = saveOvpn(server)
    vpn_process = connect(path_ovpn)
    return vpn_process

def save_temp_html(response, name='Error'):

    with open(f"./{name}.html", "w", encoding='UTF-8') as f:
        f.write(response.text)

def build_url(keyword, alliances=[], start=0):

    q = f"{keyword}"

    # 문자열 합치기
    if alliances:
        alliances = map(lambda a: f"\"{a}\"", alliances)
        alliances = " + ".join(list(alliances))
        q = q + f" + {alliances}"

    # 한글 문자등을 주소에 맞는 규격으로 변환
    q = quote_plus(q)
    url = f"https://www.google.com/search?q={q}&tbm=nws"
    if start:
        url = url + f"&start={start}"
    return url

def extr_href(elements, css_selector):
    res = elements.select(css_selector)
    return res.pop().get('href', '') if res else ''

def extr_text(elements, css_selector):
    res = elements.select(css_selector)
    return res.pop().text if res else ''

def read_xlsx_rows(path_xlsx, sheet_name='Sheet1', column = 'B'):
    wb = openpyxl.load_workbook(path_xlsx)
    sheet = wb[sheet_name]
    return [ cell.value for cell in sheet[column] ]

def get_result_stats(soup, cs_result_stats):

    result_stats = soup.select(cs_result_stats)
    if not len(result_stats):
        return 0

    result_stats = result_stats.pop().text.replace(',', '')
    result_stats = list(map(int, filter(
        lambda s: s and s.isdigit(),
        re.findall(r"(\d*)", result_stats)
    )))[0]

    return result_stats

def crawling_google_news(keyword, alliances, max_search=100, idle_sec=2):

    # Setup Headers
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.229 Whale/2.10.123.42 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8"
    }

    # Setup Cookies
    session = requests.Session()
    googleTrendsUrl = 'https://google.com'
    response = session.get(googleTrendsUrl, headers=headers)

    cookies = dict()
    if response.status_code == 200:
        cookies = response.cookies.get_dict()
    else:
        print(f"Failed get cookies - {response.status_code}")

    results = []
    n_searched = 0
    n_search = n_searched + max_search
    while n_search > n_searched:

        sleep(idle_sec)

        url = build_url(keyword, alliances=alliances, start=n_searched)
        response = session.get(url, headers=headers, cookies=cookies)

        code = response.status_code
        if code != 200:
            print(f"Status code : {code} -> STOP Crawling")
            return results, code

        soup = BeautifulSoup(response.content, 'html.parser', from_encoding='utf-8')
        news_cards = soup.select(cs_root)
        result_stats = get_result_stats(soup, cs_result_stats)
        n_search = result_stats if result_stats < n_search else n_search

        if len(news_cards) == 0:
            print(f"No news searched {ceo_name}, save temporal html")
            save_temp_html(response, f"NoResult_{ceo_name}")
            return results, 0

        for news_card in news_cards:

            results.append(dict(
                title = extr_text(news_card, cs_title),
                date = extr_text(news_card, cs_date),
                press = extr_text(news_card, cs_press),
                summary = extr_text(news_card, cs_summary),
                link = extr_href(news_card, cs_link),
            ))

            n_searched += 1
        print(f"{n_searched:>4}/{n_search:>4}- {keyword}")

    return results, code

def get_processed_keywords(ext='.csv'):
    processed_keywords = filter(
        lambda file_name: file_name.endswith(ext),
        listdir(DIR_NEWS_CRAWLING) )
    processed_keywords = map(
        lambda file_name: file_name.replace(ext, ''),
        processed_keywords )
    return list(processed_keywords)

if __name__ == '__main__':

    # Setup VPN
    vpn_ps = connect_vpn()

    path_xlsx  = './firmlist_210807.xlsx'
    ceo_names = read_xlsx_rows(path_xlsx)[1:]

    MAX_SEARCH = 200

    processed_keywords = get_processed_keywords()

    q_keyword = Queue()
    for ceo_name in ceo_names:
        keyword = f"{ceo_name} CEO"
        if keyword.replace(' ', '_') not in processed_keywords:
            q_keyword.put(keyword)

    while not q_keyword.empty():
        try:
            keyword = q_keyword.get_nowait()

            print(f"Start Crawling {keyword}")
            results, code = crawling_google_news(
                keyword=keyword,
                alliances=[],
                max_search=MAX_SEARCH,
                idle_sec=IDLE
            )

            if code == 200:
                path_csv = path.join(DIR_NEWS_CRAWLING, keyword.replace(' ', '_')+'.csv')
                pd.DataFrame(results).to_csv(path_csv, index=False, encoding='utf-8-sig')
                print(f"Save Crawling results {keyword}\n- at: {path_csv}")

            elif code == 0:
                print(f"No search results {keyword}")

            elif code == 429:
                my_ip = get_external_ip()
                print(f"You IP has been baned: {my_ip}")
                vpn_ps.terminate()
                vpn_ps = connect_vpn()
                q_keyword.put(keyword)

            else:
                print(f"Error {keyword} - {code}")

        except Exception as e:
            print(e)
            print('Disconnect VPN')
            vpn_ps.terminate()
