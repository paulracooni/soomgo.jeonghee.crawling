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

IDLE = 1.5

cs_root = "#rso > g-card  div.dbsr"

cs_link = "a"

cs_press = "div.XTjFC.WF4CUc"

cs_title = "div.JheGif.nDgy9d"

cs_summary = "div.Y3v8qd"

cs_date = "div.wxp1Sb > span"

cs_result_stats = "#result-stats"

import re
from time import sleep

import requests
from urllib.parse import quote_plus
from bs4 import BeautifulSoup

import openpyxl
import pandas as pd

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
    result_stats = soup.select(cs_result_stats).pop().text.replace(',', '')

    result_stats = list(map(int, filter(
        lambda s: s and s.isdigit(),
        re.findall(r"(\d*)", result_stats)
    )))[0]
    return result_stats

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.229 Whale/2.10.123.37 Safari/537.36"
}


path_xlsx  = './firmlist_210807.xlsx'
ceo_names = read_xlsx_rows(path_xlsx)[1:]


n_search = 100
extracted = []
for ceo_name in ceo_names:

    n_searched = 0

    while n_search > n_searched:

        url = build_url(f"{ceo_name} CEO", start=n_searched)
        sleep(1)
        response = requests.get(url, headers=headers)

        result_stats = get_result_stats(soup, cs_result_stats)
        n_search = result_stats if result_stats < n_search else n_search

        code = response.status_code
        if code == 200:
            pass
        else:
            print(f"Status code : {code} -> STOP Crawling")
            break
        soup = BeautifulSoup(response.text, 'html.parser')

        news_cards = soup.select(cs_root)

        for news_card in news_cards:

            extracted.append(dict(
                link = extr_href(news_card, cs_link),
                press = extr_text(news_card, cs_press),
                title = extr_text(news_card, cs_title),
                summary = extr_text(news_card, cs_summary),
                date = extr_text(news_cards, cs_date)
            ))

            n_searched += 1
            print(f"{n_searched:>4}/{n_search:>4}- {ceo_name}")
#%%


pd.DataFrame(extracted)[
    ['title', 'date', 'press', 'summary', 'link']
].to_csv("restuls.csv", index=False)

#%%