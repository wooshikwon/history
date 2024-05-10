#!/usr/bin/env python
# coding: utf-8

# In[50]:


import pyproj
from shapely.geometry import MultiPoint, LineString
from shapely.ops import transform
from functools import partial
import pandas as pd
from tqdm import tqdm

import os


# In[49]:


import config
from packages import *


# In[51]:


def transform_to_kilometer(polygon):
    project = partial(
        pyproj.transform,
        pyproj.Proj('epsg:4326'),  # 원본 좌표계 (위도, 경도)
        pyproj.Proj('epsg:3857')  # 목표 좌표계 (미터 단위)
    )
    return transform(project, polygon)


# In[52]:


class create_convexhull:
    def __init__(self, path_class):
        self.path_class = path_class
        self.preprocessed_path = path_class.preprocessed_path
        self.result_path_ymd = path_class.result_path_ymd
        self.lastsunday_str = get_lastsunday(path_class.ymd)

    def data_load(self):
        filtered_path = f'{self.preprocessed_path}/filtered_{self.lastsunday_str}.parquet'
        allpoints_path = f'{self.preprocessed_path}/allpoints_{self.lastsunday_str}.parquet'

        if os.path.isfile(filtered_path):
            self.filtered = pd.read_parquet(filtered_path)  # Save using the full path
        else:
            print(f'There is no file : filtered_{self.lastsunday_str}.parquet')
        
        if os.path.isfile(allpoints_path):
            self.allpoints = pd.read_parquet(allpoints_path)  # Save using the full path
        else:
            print(f'There is no file : allpoints_{self.lastsunday_str}.parquet')

    def convexhull(self):
        # 결과를 저장할 빈 DataFrame 초기화
        self.result_df = pd.DataFrame(columns=['ord_date_ymd', 'br_code', 'area_in_meters', 'polygon'])
        min_size = self.allpoints.groupby(['ord_date_ymd', 'cth_br_code']).size()
        valid_hurbs = min_size[min_size > 3].index

        rows = []

        for ord_date_ymd, code in tqdm(valid_hurbs):
            points_df = self.allpoints[(self.allpoints['ord_date_ymd'] == ord_date_ymd) & (self.allpoints['cth_br_code'] == code)]
            points = points_df[['latitude', 'longitude']].values

            polygon = MultiPoint(points).convex_hull  # Convex Hull 생성
            transformed_polygon = transform_to_kilometer(polygon)  # 좌표계 변환
            area_in_meters = transformed_polygon.area / 1000000  # 제곱킬로미터 단위 면적

            if polygon.geom_type == 'Polygon':
                polygon_coords = list(polygon.exterior.coords)
            elif polygon.geom_type == 'LineString':
                polygon_coords = list(polygon.coords)
            else:
                polygon_coords = [(polygon.x, polygon.y)]

            # 결과 리스트에 행 추가
            rows.append({
                'ord_date_ymd': ord_date_ymd,
                'br_code': code,
                'area_in_meters': area_in_meters,
                'polygon': polygon_coords
            })

        # 결과 DataFrame에 행 추가
        self.result_df = pd.concat([self.result_df, pd.DataFrame(rows)], ignore_index=True)

    def merge(self):
        # 그룹화하여 계산
        grouped = self.filtered.groupby(['ord_date_ymd', 'cth_br_code']).agg(
            avg_finish_time=('finish_time', 'mean'),
            ratio_under_40=('finish_time', lambda x: (x < 40).mean()),
            unique_wk_code=('cth_wk_code', 'nunique'),
            cnts=('ord_no', 'nunique')
        ).reset_index()

        merged_df = pd.merge(grouped, self.result_df, how='left', left_on=['ord_date_ymd', 'cth_br_code'], right_on=['ord_date_ymd', 'br_code'])
        merged_df['density_index'] = (merged_df['cnts'] * merged_df['area_in_meters']) / (merged_df['unique_wk_code'])
        
        merged_df.to_parquet(self.result_path_ymd, index=False)
    
    def __call__(self):
        self.data_load()
        self.convexhull()
        self.merge()


# In[53]:


def path_class(ymd):
    file_class = config.path_class(ymd)
    return file_class

# 본 파일(loaddata.py)의 데이터 로드 Class를 선언하고, 실행 함수
def main(file_class):    
    run_class = create_convexhull(file_class) #brand는 이 스크립트의 특이 추가 인자
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

