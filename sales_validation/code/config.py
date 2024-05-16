#!/usr/bin/env python
# coding: utf-8

# In[2]:


import query
import security


# In[3]:


import os
import datetime

from packages import *


# In[4]:


class path_class:
    def __init__(self, ymd):
        
        self.ymd = ymd
        self.ymd_str = format_date(ymd)

        # 디렉토리 path
        self.top_path = os.path.expanduser('~/Desktop/work/sales_validation')
        self.data_path = f'{self.top_path}/data'
        self.data_path_ymd = f'{self.top_path}/data/{self.ymd_str}'

        self.raw_path = f'{self.data_path_ymd}/raw'
        self.preprocessed_path = f'{self.data_path_ymd}/preprocessed'

        self.upload_path = f'{self.data_path}/upload'
        
        self.result_path = f'{self.top_path}/result'
        self.result_path_ymd = f'{self.top_path}/result/{self.ymd_str}'

        # 디렉토리 생성
        os.makedirs(self.top_path, exist_ok=True)     
        os.makedirs(self.raw_path, exist_ok=True)     
        os.makedirs(self.preprocessed_path, exist_ok=True)
        os.makedirs(self.upload_path, exist_ok=True) 
        os.makedirs(self.result_path, exist_ok=True)
        os.makedirs(self.result_path_ymd, exist_ok=True)

