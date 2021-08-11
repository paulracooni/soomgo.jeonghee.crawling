import re
from tqdm import tqdm
from time import sleep
from bs4 import BeautifulSoup
from urllib.parse import quote_plus

from newsplease import NewsPlease
from .CrawlerBase import CrawlerBase

'#main > div:nth-child(5) > div > div:nth-child(1) > a'

class CrawlerGoogleNews(CrawlerBase):

    cs_links        = [
        "a.fuLhoc",
        "#rso g-card a",
        "#main div a"
    ]


    def __init__(self,
        base_url        = "https://www.google.com",
        result_per_page = 10,
        use_vpn         = True,
        idle_sec        = 2,
        debug_dir       = '',
    ):

        self.use_vpn         = use_vpn
        self.base_url        = base_url
        self.result_per_page = result_per_page
        self.idle_sec        = idle_sec
        self.debug_dir       = debug_dir
        self.reset()

    def test(self, keyword, lang='en', max_search=500):
        url = self.__build_url(keyword, start=0, lang=lang)
        response = self.get(url)
        return response

    def run(self, keyword, lang='en', max_search=500, verbose=True):

        if verbose: pbar = tqdm(total=max_search)

        results, n_searched = [], 0
        while n_searched < max_search:

            sleep(self.idle_sec)

            # Build URL for google news search
            url = self.__build_url(keyword, start=n_searched, lang=lang)

            # Request[GET]
            response = self.get(url)

            # Parse lists
            soup = BeautifulSoup(response.content, 'html.parser', from_encoding='utf-8')
            news_urls = self.__extr_news_urls(soup)

            if len(news_urls) == 0:
                self.save_response_as_html(response, "no_news_cards")
                return results

            for news_url in news_urls:

                article_html = self.get(news_url).content
                article = NewsPlease.from_html(article_html)

                if article.maintext == None or article.language != lang:
                    continue

                results.append(dict(
                    keyword       = keyword,
                    source_domain = article.source_domain,
                    date_publish  = article.date_publish,
                    language      = article.language,
                    title         = article.title,
                    maintext      = article.maintext,
                    url           = url,
                ))
                n_searched += 1

                if verbose:
                    pbar.update(1)
                    pbar.set_description(article.title[:10]+'...')

                if n_searched < max_search:
                    break

        if verbose: pbar.close()

        return results

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
            if not href.startswith('http'):
                href = self.base_url + href
            news_card_urls.append(href)

        return news_card_urls

    def __extr_link(self, news_card):

        return news_card.get('href', '')

    def __build_url(self, keyword, start=0, lang='en'):

        url = f"{self.base_url}/search?"+\
              f"&q={quote_plus(keyword)}"+\
              f"&tbm=nws"+\
              f"&hl={lang}"+\
              f"&num={self.result_per_page}"

        url = url + f"&start={start}" if start else url

        return url

