#!/usr/bin/env python
# coding: utf-8

# In[3]:
import query
import security
from packages import *

import os
import datetime


# In[4]:


class path_class:
    def __init__(self, ymd):

        self.ymd = ymd
        self.lastsunday_str = get_lastsunday(self.ymd)

        # 디렉토리 path
        self.top_path = os.path.expanduser('~/Desktop/work/area_density')
        self.data_path = f'{self.top_path}/data'
        self.data_path_ymd = f'{self.top_path}/data/{self.lastsunday_str}'

        self.raw_path = f'{self.data_path_ymd}/raw'
        self.preprocessed_path = f'{self.data_path_ymd}/preprocessed'

        self.result_path = f'{self.top_path}/result'
        self.result_path_ymd = f'{self.top_path}/result/{self.lastsunday_str}'

        # 디렉토리 생성
        os.makedirs(self.top_path, exist_ok=True)     
        os.makedirs(self.result_path, exist_ok=True)
        os.makedirs(self.result_path_ymd, exist_ok=True)
        os.makedirs(self.raw_path, exist_ok=True)     
        os.makedirs(self.preprocessed_path, exist_ok=True)

