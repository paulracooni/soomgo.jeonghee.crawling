import re
import requests
from tqdm import tqdm
from time import sleep
from bs4 import BeautifulSoup
from urllib.parse import quote_plus

from newsplease import NewsPlease
from .CrawlerBase import CrawlerBase
from .utils import get_user_agent

class CrawlerGoogleNews(CrawlerBase):

    cs_links        = [
        "a.fuLhoc",
        "#rso g-card a",
        "#main div a"
    ]


    def __init__(self,
        base_url        = "https://www.google.com",
        test_url        = "https://www.google.com/search?tbm=nws&q=hello",
        result_per_page = 100,
        use_vpn         = True,
        idle_sec        = 2,
        debug_dir       = '',
        verbose         = True,
    ):

        self.use_vpn         = use_vpn
        self.base_url        = base_url
        self.test_url        = test_url
        self.result_per_page = result_per_page
        self.idle_sec        = idle_sec
        self.debug_dir       = debug_dir
        self.verbose         = verbose
        self.reset()

    def set_headers(self):
        assert self.base_url, "Please set self.base_url"
        self.headers = {
            'user-agent': get_user_agent(),
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
            'referer'        : self.base_url
        }

    def set_cookies(self):
        self.cookies = dict()

    def test(self, keyword, lang='en', max_search=500):
        url = self.__build_url(keyword, start=0, lang=lang)
        response = self.get(url)
        return response

    def run(self, keyword, lang='en', max_search=500):

        url = self.__build_url(keyword, start=0, num=max_search, lang=lang)
        response, _ = self.get(url)
        if not isinstance(response, requests.Response):
            return []
        soup = BeautifulSoup(response.content, 'html.parser', from_encoding='utf-8')
        news_urls = self.__extr_news_urls(soup)

        return news_urls

    def __build_url(self, keyword, start=0, num=100,lang='en'):

        url = f"{self.base_url}/search?"+\
              f"&tbm=nws"+\
              f"&hl={lang}"+\
              f"&q={quote_plus(keyword)}"+\
              f"&num={num}"

        url = url + f"&start={start}" if start else url

        return url

    def __extr_news_urls(self, soup):

        news_cards = []
        for cs_link in self.cs_links:
            news_cards = soup.select(cs_link)
            if news_cards:
                break

        if not news_cards:
            return []

        news_card_urls = []
        for news_card in news_cards:
            href = news_card.get('href', '')

            if href.startswith('/url?q='):
                href = href.replace('/url?q=', '')

            if '&' in href:
                href = href[:href.find('&')]

            if href.startswith('http') and 'google.com' not in href:
                news_card_urls.append(href)


        return news_card_urls

