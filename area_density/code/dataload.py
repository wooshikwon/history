#!/usr/bin/env python
# coding: utf-8

# In[3]:

from packages import *
import config

# In[4]:


import os
import datetime
import pandas as pd

# In[5]:


class dataload:
    def __init__(self, path_class):
        self.path_class = path_class
        self.raw_path = self.path_class.raw_path
        self.lastsunday_str = get_lastsunday(path_class.ymd)

    def data_load_save(self):
        
        file_path = os.path.join(self.raw_path, f'xydata_{self.lastsunday_str}.parquet')

        if not os.path.isfile(file_path):
            raw_df = pd.read_sql_query(config.query.xydata_query(self.lastsunday_str), config.security.aws_conn)
            raw_df.to_parquet(file_path, index=False)  # Save using the full path
        else:
            pass

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
    parser.add_argument('--ymd', type=str, default=datetime.datetime.now().strftime('%Y%m%d'))
    args, unknown = parser.parse_known_args()
    
    run(args.ymd)

# In[ ]:



