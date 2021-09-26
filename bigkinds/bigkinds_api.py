#%%
import requests

# 뉴스 검색 API
endpoint = "http://tools.kinds.or.kr:8888/search/news"
access_key = 'fec62330-8877-476b-9b5e-a0b3b08cce7c'


data = {
    "access_key": access_key,
    "argument": {
        "query": "서비스 AND 출시",
        "published_at": {
            "from": "2019-01-01",
            "until": "2019-03-31"
        },
        "provider": [
            "경향신문",
        ],
        "category": [
            "정치>정치일반",
            "IT_과학"
        ],
        "category_incident": [
            "범죄",
            "교통사고",
            "재해>자연재해"
        ],
        "byline": "",
        "provider_subject": [
            "경제", "부동산"
        ],
        "subject_info": [
            ""
        ],
        "subject_info1": [
            ""
        ],
        "subject_info2": [
            ""
        ],
        "subject_info3": [
            ""
        ],
        "subject_info4": [
            ""
        ],
        "sort": {"date": "desc"},
        "hilight": 200,
        "return_from": 0,
        "return_size": 5,
        "fields": [
            "byline",
            "category",
            "category_incident",
            "provider_news_id"
        ]
    }
}

results = requests.post(endpoint, data, timeout=5)
results