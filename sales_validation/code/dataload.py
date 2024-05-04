#!/usr/bin/env python
# coding: utf-8

# In[3]:


import config
from packages import *

# In[4]:


import os
import datetime
import pandas as pd

# In[5]:


class dataload:
    def __init__(self, path_class):
        self.path_class = path_class
        self.raw_path = self.path_class.raw_path
        self.ymd = format_date(path_class.ymd)

    def data_load_save(self):
        query_list = ['hq_profit', 'market_size', 'new_hurbs', 'churned_hurbs', 'new_b2bstores', 'churned_b2bstores']

        for name in query_list:
            
            query_name = f'{name}_query'
            file_path = os.path.join(self.raw_path, f'{name}_{self.ymd}.csv')

            if not os.path.isfile(file_path):
                query_function = getattr(config.query, query_name)
                raw_df = pd.read_sql_query(query_function(self.ymd), config.security.aws_conn)
                raw_df.to_csv(file_path, index=False)  # Save using the full path
            else:
                raw_df = pd.read_csv(file_path, index_col=False)  # Use the full path here, correct index_col to index

    def __call__(self):
        self.data_load_save()

# In[6]:


# config.py의 path Class
# packages, __init__.py의 Logger를 얻는 함수.
def path_class(ymd):
    file_class = config.path_class(ymd)
    '''
    'os.path.basename(os.path.abspath(__file__)) 
    이 코드는 현재 실행 중인 Python 파일의 절대 경로에서 파일 이름을 추출하는 역할을 합니다. 
    각 부분을 자세히 살펴보면:

		__file__ - 이것은 현재 실행 중인 스크립트의 파일 이름을 포함하는 Python 내장 변수입니다. 
							이 변수에는 스크립트의 경로가 상대적일 수도 있고 절대적일 수도 있습니다.
		os.path.abspath(__file__) - __file__ 변수에 저장된 경로를 절대 경로로 변환합니다. 
																즉, 파일 시스템의 루트부터 시작하는 전체 경로를 반환합니다.
		os.path.basename(path) - 주어진 경로에서 파일 이름만 추출합니다. 
		
		따라서 이 함수는 os.path.abspath(__file__)에 의해 생성된 절대 경로에서 마지막 부분, 즉 파일의 이름을 반환합니다.

		예를 들어, 스크립트의 절대 경로가 /home/user/scripts/my_script.py라면, 
		os.path.basename(os.path.abspath(__file__))는 my_script.py를 반환합니다. 
		이렇게 파일 이름을 추출하는 이유는 보통 로깅, 설정 파일 저장 등에서 
		현재 실행 중인 스크립트 기반으로 경로나 파일 이름을 설정할 때 유용하게 사용됩니다.
		'''
    
    return file_class

# 본 파일(loaddata.py)의 데이터 로드 Class를 선언하고, 실행 함수
def main(file_class):    
    run_class = dataload(file_class) #brand는 이 스크립트의 특이 추가 인자
    run_class()    

# 스크립트 실행함수
def run(ymd):
    file_class = path_class(ymd)
    main(file_class)

# input 입력 조작 및 run 함수 실행
if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--ymd', type=str, default=datetime.datetime.now().strftime('%Y%m%d'))
    args, unknown = parser.parse_known_args()
    
    run(args.ymd)

# In[ ]:



