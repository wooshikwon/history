#!/usr/bin/env python
# coding: utf-8

# In[3]:


import config
from packages import *

# In[4]:


import os
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import pandas as pd

# In[5]:

class dataload:
    def __init__(self, path_class):
        self.path_class = path_class
        self.raw_path = self.path_class.raw_path

        self.ymd = format_date(path_class.ymd)
        self.previous_ymd = get_previous_ymd(path_class.ymd)

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
        
        # 전월 기준 신규/이탈및휴면 허브와 상점 데이터도 추가적으로 저장
        previous_month_query_list = ['new_hurbs', 'churned_hurbs', 'new_b2bstores', 'churned_b2bstores']

        for name2 in previous_month_query_list:
            
            query_name = f'{name2}_query'
            file_path = os.path.join(self.raw_path, f'previous_{name2}_{self.ymd}.csv')

            if not os.path.isfile(file_path):
                query_function = getattr(config.query, query_name)
                raw_df = pd.read_sql_query(query_function(self.previous_ymd), config.security.aws_conn)
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
    parser.add_argument('--ymd', type=str, default=datetime.now().strftime('%Y%m%d'))
    args, unknown = parser.parse_known_args()
    
    run(args.ymd)

# In[ ]:



