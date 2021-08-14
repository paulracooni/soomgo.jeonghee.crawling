from time import sleep
from bs4 import BeautifulSoup

from newsplease import NewsPlease
from .CrawlerBase import CrawlerBase
from .utils import get_user_agent

class CrawlerNewsPlease(CrawlerBase):

    def __init__(self,
        base_url        = "https://www.google.com",
        test_url        = "",
        use_vpn         = True,
        idle_sec        = 2,
        debug_dir       = '',
        verbose         = True,
    ):

        self.use_vpn         = use_vpn
        self.base_url        = base_url
        self.test_url        = test_url
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

    def run(self, url):
        response, code = self.get(url)
        if code != 200: return None
        html = response.content
        article = NewsPlease.from_html(html)
        return article