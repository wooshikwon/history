#!/usr/bin/env python
# coding: utf-8

# In[3]:


import datetime
import os
import time
import subprocess
import argparse
from dateutil.relativedelta import relativedelta


# In[6]:


def file_remove(top_path):
    # 현재 날짜를 구합니다.
    current_date = datetime.datetime.now()
    data_directory = os.listdir(f'{top_path}/data')

    # 주어진 디렉토리 내의 모든 파일에 대해 반복합니다.
    for directoryname in data_directory:
        try:
            date_str = directoryname.split('_')[-1].replace('.parquet', '')
            file_date = datetime.datetime.strptime(date_str, '%Y-%m-%d')

            # 파일의 날짜가 현재 날짜의 4주 전보다 이전이면 파일을 삭제합니다.
            if file_date < current_date - relativedelta(weeks=4):
                os.remove(os.path.join(data_directory, directoryname))

        except ValueError as e:
            pass

# In[ ]:


def run(ymd):
    
    top_path = os.path.expanduser('~/Desktop/work/area_density')
    file_remove(top_path)
    
    # Step 1
    subprocess.call(f"python {top_path}/code/dataload.py --ymd {ymd}", shell=True)
    time.sleep(60)
    
    # Step 2
    subprocess.call(f"python {top_path}/code/preprocessor.py --ymd {ymd}", shell=True)
    time.sleep(60)
    
    # Step 3
    subprocess.call(f"python {top_path}/code/create_convexhull.py --ymd {ymd}", shell=True)
    time.sleep(60)

if __name__ == '__main__':
    
    parser = argparse.ArgumentParser()
    parser.add_argument('--ymd', type=str, default=datetime.datetime.now().strftime('%Y%m%d'))
    
    args, unknown = parser.parse_known_args()
    
    run(args.ymd)

