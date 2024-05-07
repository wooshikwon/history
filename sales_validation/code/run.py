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
    raw_files = os.listdir(f'{top_path}/data/raw')
    preprocessed_files = os.listdir(f'{top_path}/data/preprocessed')

    # 주어진 디렉토리 내의 모든 파일에 대해 반복합니다.
    for filename in raw_files:
        if filename.endswith('.csv'):
            try:
                date_str = filename.split('_')[-1].replace('.csv', '')
                file_date = datetime.datetime.strptime(date_str, '%Y-%m-%d')

                # 파일의 날짜가 현재 날짜의 4개월 전보다 이전이면 파일을 삭제합니다.
                if file_date <= current_date - relativedelta(months=4):
                    os.remove(os.path.join(f'{top_path}/data/raw', filename))

            except ValueError as e:
                pass
    
    for filename in preprocessed_files:
        if filename.endswith('.csv'):
            try:
                date_str = filename.split('_')[-1].replace('.csv', '')
                file_date = datetime.datetime.strptime(date_str, '%Y-%m-%d')

                # 파일의 날짜가 현재 날짜의 4개월 전보다 이전이면 파일을 삭제합니다.
                if file_date <= current_date - relativedelta(months=4):
                    os.remove(os.path.join(f'{top_path}/data/preprocessed', filename))

            except ValueError as e:
                pass


# In[ ]:


def run(ymd):
    
    top_path = os.path.expanduser('~/Desktop/work/sales_validation')
    file_remove(top_path)
    
    # Step 1
    subprocess.call(f"python {top_path}/code/dataload.py --ymd {ymd}", shell=True)
    time.sleep(60)
    
    # Step 2
    subprocess.call(f"python {top_path}/code/preprocessor.py --ymd {ymd}", shell=True)
    time.sleep(60)
    
    # Step 3
    subprocess.call(f"python {top_path}/code/calculate_result.py --ymd {ymd}", shell=True)
    time.sleep(60)

if __name__ == '__main__':
    
    parser = argparse.ArgumentParser()
    parser.add_argument('--ymd', type=str, default=datetime.datetime.now().strftime('%Y%m%d'))
    
    args, unknown = parser.parse_known_args()
    
    run(args.ymd)

