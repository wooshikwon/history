#!/usr/bin/env python
# coding: utf-8

# In[7]:


import os
import pandas as pd
import numpy as np
from datetime import datetime
from tqdm import tqdm
from scipy.spatial import KDTree

import warnings
warnings.filterwarnings('ignore')


# In[8]:


import config
from packages import *


# In[11]:


class preprocessor:
    def __init__(self, path_class):
        self.path_class = path_class
        self.raw_path = self.path_class.raw_path
        self.preprocessed_path = self.path_class.preprocessed_path
        self.lastsunday_str = get_lastsunday(path_class.ymd)

    def data_load(self):
        file_path = os.path.join(self.raw_path, f'xydata_{self.lastsunday_str}.parquet')

        if os.path.isfile(file_path):
            self.df = pd.read_parquet(file_path)  # Save using the full path
        else:
            print('There is no file : xydata_{self.lastsunday_str}.parquet')

    def remove_outlier(self):
        file_path = os.path.join(self.preprocessed_path, f'filtered_{self.lastsunday_str}.parquet')

        if not os.path.isfile(file_path):
            # 청크 크기 설정
            chunk_size = 10000  # 10,000개의 행으로 청크를 나눔
            num_chunks = len(self.df) // chunk_size + 1  # 청크의 총 개수 계산

            # 결과를 저장할 빈 DataFrame 초기화
            self.filtered_df = pd.DataFrame()

            # 청크별로 데이터 처리
            for i in tqdm(range(num_chunks)):
                # 청크 분할
                df_chunk = self.df[i*chunk_size:(i+1)*chunk_size]
                
                # 날짜 컬럼 datetime으로 변환
                df_chunk['ord_date'] = pd.to_datetime(df_chunk['ord_date'])
                df_chunk['cth_date'] = pd.to_datetime(df_chunk['cth_date'])
                df_chunk['pickup_date'] = pd.to_datetime(df_chunk['pickup_date'], errors='coerce')
                df_chunk['finish_date'] = pd.to_datetime(df_chunk['finish_date'])
                df_chunk['km_product'] = df_chunk['km_product'].astype(float)

                # 좌표값 실수형으로 변환
                df_chunk['sa_map_x'] = df_chunk['sa_map_x'].astype(float)
                df_chunk['sa_map_y'] = df_chunk['sa_map_y'].astype(float)
                df_chunk['ea_map_x'] = df_chunk['ea_map_x'].astype(float)
                df_chunk['ea_map_y'] = df_chunk['ea_map_y'].astype(float)
                
                # 이상치 제거 - 조건에 맞는 데이터만 필터링
                # 발주 완료까지 5분 초과 데이터만
                df_chunk = df_chunk[(df_chunk['finish_date'] - df_chunk['ord_date']).dt.seconds > 300]

                # 4.5km 미만 배달건만
                df_chunk = df_chunk[(df_chunk['km_product'] > 0) & (df_chunk['km_product'] < 4500)]

                # 발주~완료까지 시속 60km/h 미만 배달건만
                df_chunk = df_chunk[((df_chunk['km_product'] / 1000) / ((df_chunk['finish_date'] - df_chunk['ord_date']).dt.seconds / 3600)) < 60]
                df_chunk = df_chunk[(df_chunk['delivery_price'] > 2500) & (df_chunk['delivery_price'] < 12500)]
                
                # 컬럼 생성
                df_chunk['finish_time'] = (df_chunk['finish_date'] - df_chunk['ord_date']).dt.seconds / 60 # 발주~완료시간
                
                # 결과 병합
                self.filtered_df = pd.concat([self.filtered_df, df_chunk], ignore_index=True)

            self.filtered_df = self.filtered_df.dropna(subset=['sa_map_x', 'sa_map_y', 'ea_map_x', 'ea_map_y']).reset_index(drop=True)
            self.filtered_df.to_parquet(file_path, index=False)
            print(f'File saved : filtered_{self.lastsunday_str}.parquet')  # Save using the full path
        else:
            self.filtered_df = pd.read_parquet(file_path)
            print(f'File already exists: filtered_{self.lastsunday_str}.parquet')


    def remove_lowdensityxy(self):
        file_path = os.path.join(self.preprocessed_path, f'allpoints_{self.lastsunday_str}.parquet')

        if not os.path.isfile(file_path):
            # 출발지와 도착지 좌표를 구분 없이 하나의 점으로 취급
            start_points = self.filtered_df[['ord_date_ymd', 'brand', 'cth_br_code', 'ord_no', 'sa_map_x', 'sa_map_y']].rename(columns={'sa_map_x': 'longitude', 'sa_map_y': 'latitude'})
            end_points = self.filtered_df[['ord_date_ymd', 'brand', 'cth_br_code', 'ord_no', 'ea_map_x', 'ea_map_y']].rename(columns={'ea_map_x': 'longitude', 'ea_map_y': 'latitude'})

            self.all_points = pd.concat([start_points, end_points], axis=0)

            # 각 brand, cth_br_code별로 전체 건수 구하기
            self.all_points['count'] = self.all_points.groupby(['ord_date_ymd', 'brand', 'cth_br_code'])['ord_no'].transform('count')

            # 3% 기준을 위한 임계값 구하기
            self.all_points['threshold'] = self.all_points['count'] * 0.01

            # 결과를 저장할 리스트
            to_drop = []

            # 각 ord_date_ymd, brand, cth_br_code 그룹별로 반복
            for (ord_date_ymd, brand, cth_br_code), group in tqdm(self.all_points.groupby(['ord_date_ymd', 'brand', 'cth_br_code'])):
                # KDTree를 사용하기 위해 (lat, lng) 좌표 배열 생성
                coords = group[['latitude', 'longitude']].values
                tree = KDTree(coords)

                # 각 row에 대해 탐색
                for row in group.itertuples():
                    # KDTree를 사용하여 반경 300m 내의 점들을 찾음
                    indices = tree.query_ball_point([row.latitude, row.longitude], 0.0045)  # 0.0045 degrees is roughly 500 meters (x = 500/111000)

                    if len(indices) == 0:
                        to_drop.append(row.Index)
                        
                    else:
                        # 동일한 brand, cth_br_code를 가진 ord_no의 수 계산
                        same_brand_code_df = group.iloc[indices]

                        # 전체 건수 대비 5% 미만인지 확인
                        if same_brand_code_df.shape[0] < row.threshold:
                            to_drop.append(row.Index)

            # 해당 row 삭제
            self.all_points.drop(to_drop, inplace=True)

            # self.all_points.drop(columns=['count', 'threshold'], inplace=True)
            self.all_points.to_parquet(file_path, index=False)  # Save using the full path
            print(f'File saved : allpoints_{self.lastsunday_str}.parquet')
        else:
            print(f'File already exists: allpoints_{self.lastsunday_str}.parquet')

    def __call__(self):
        self.data_load()
        self.remove_outlier()
        self.remove_lowdensityxy()


# In[12]:


def path_class(ymd):
    file_class = config.path_class(ymd)
    return file_class

# 본 파일(loaddata.py)의 데이터 로드 Class를 선언하고, 실행 함수
def main(file_class):    
    run_class = preprocessor(file_class) #brand는 이 스크립트의 특이 추가 인자
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

