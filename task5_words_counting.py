"""
[Subject-1 1차 Crawling]
- 부정어를 계수한
- 어느 CEO가 부정어를 몇개 가지고 있다.
- OUTPUT: CEO이름, 부정어 개수, 해당 부정어의 링크

[Subject-2. 2차 Crawling]
- Maintext에서, Company name, Aliance, Partner 키워드 유무로 기사 필터링

"""
#%%
"""[Subject1]
- 1. 크롤링된 1st_Company_CEO Excel 파일 읽기
- 2. LoughranMcDonald_SentimentWordLists_2018 Excel 파일에서 부정어 추출하기
- 3. 크롤링 Excel 파일에서, Maintext 추출 후, 각 행을 토큰화
- 4. 토큰화된 단어셋과, 부정어 셋 intersect 연산으로 쿼리
- 5. 각 기사별로, 부정어 개수 Count
- 6. 출력 Columns 정의 후, 데이터 정리
- 7. 정리된 데이터 Excel로 정리
"""
# Find all, Aliance
# 연관이 있는것, Aliance와 Partnership 단어를 찾아난다 
from os import path, makedirs

import nltk
import numpy as np
import pandas as pd

# 1. 크롤링된 1st_Company_CEO Excel 파일 읽기
def load_crawled_data_as_df(
    path_xlsx = "./datas/inputs/task5/1st_Company_CEO.xlsx"
):
    with open(path_xlsx, 'rb') as f:
        df = pd.read_excel(f, sheet_name=0, engine='openpyxl')
    return df


def load_negative_words(
    path_xlsx="./datas/inputs/task5/LoughranMcDonald_SentimentWordLists_2018.xlsx"
):
    with open(path_xlsx, 'rb') as f:
        df = pd.read_excel(f, sheet_name='Negative', engine='openpyxl', header=None)
    return df.values.flatten()

# 3. 크롤링 Excel 파일에서, Maintext 추출 후, 각 행을 토큰화


#%%
# 1. 크롤링된 1st_Company_CEO Excel 파일 읽기
path_xlsx = "./datas/inputs/task5/1st_Company_CEO.xlsx"
with open(path_xlsx, 'rb') as f:
    df_crawled = pd.read_excel(f, sheet_name=0, engine='openpyxl')

# 2. LoughranMcDonald_SentimentWordLists_2018 Excel 파일에서 부정어 추출하기
path_xlsx="./datas/inputs/task5/LoughranMcDonald_SentimentWordLists_2018.xlsx"
with open(path_xlsx, 'rb') as f:
    neg_words = pd.read_excel(f, sheet_name='Negative', engine='openpyxl', header=None)
neg_words = neg_words.values.flatten()

# 3. 크롤링 Excel 파일에서, Maintext 추출 후, 각 행을 토큰화
df_crawled['tokens'] = df_crawled.maintext.apply(lambda s: nltk.word_tokenize(str(s)))


# 4. 토큰화된 단어셋과, 부정어 셋 intersect 연산으로 쿼리
df_crawled['neg_words'] = df_crawled.tokens.apply(
    lambda token: np.intersect1d(
        np.array(list(
            map(
                lambda s: s.upper().replace('_', ''),
                token
        ))), 
        neg_words
    ))

# 5. 각 기사별로, 부정어 개수 Count
df_crawled['count_neg_words'] = df_crawled.neg_words.apply(len)

# 6. 출력 Columns 정의 후, 데이터 정리
makedirs("./datas/outputs/task5", exist_ok=True)
path_xlsx="./datas/outputs/task5/1st_Company_CEO_NegCnt.xlsx"


with open(path_xlsx, 'wb') as f:
    df_crawled.to_excel(f, engine='openpyxl', encoding='UTF-8')
# %%