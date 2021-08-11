import numpy as np
import pandas as pd
from crawlers import CrawlerGoogleNews

crawler = CrawlerGoogleNews(
    base_url        = "https://www.google.com",
    result_per_page = 100,
    use_vpn         = False,
    idle_sec        = 2,
    debug_dir       = './',
)

response = crawler.run(
    keyword='Python',
    lang='en',
    max_search=5
)

print(pd.DataFrame(response))