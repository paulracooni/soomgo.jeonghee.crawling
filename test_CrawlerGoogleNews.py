import numpy as np
import pandas as pd
from crawlers import CrawlerGoogleNews

crawler = CrawlerGoogleNews(
    result_per_page = 10,
    use_vpn         = True,
    idle_sec        = 1,
    debug_dir       = './debug_html',
    verbose = True
)

response = crawler.run(
    keyword='Python',
    lang='en',
    max_search=5
)

test = pd.DataFrame(response)
print(test)

test.to_csv("./datas/outputs/test_crawler/test_results.csv", index=False, encoding='utf-8-sig')