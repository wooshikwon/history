#!/usr/bin/env python
# coding: utf-8

# In[50]:


import pyproj
from shapely.geometry import MultiPoint, LineString
from shapely.ops import transform
from functools import partial
import pandas as pd
import numpy as np
from tqdm import tqdm

import os


# In[49]:


import config
from packages import *


# In[51]:


def transform_to_meter(polygon):
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
        self.result_path = path_class.result_path
        self.lastsunday_str = get_lastsunday(path_class.ymd)

    def data_load(self):
        filtered_filepath = self.path_class.filtered_filepath
        allpoints_filepath = self.path_class.allpoints_filepath
        hurbinfo_filepath = self.path_class.hurbinfo_filepath

        if os.path.isfile(filtered_filepath):
            self.filtered = pd.read_parquet(filtered_filepath)  
        else:
            print(f'There is no file : filtered_{self.lastsunday_str}.parquet')
        
        if os.path.isfile(allpoints_filepath):
            self.allpoints = pd.read_parquet(allpoints_filepath) 
        else:
            print(f'There is no file : allpoints_{self.lastsunday_str}.parquet')

        if os.path.isfile(hurbinfo_filepath):
            self.hurbinfo_df = pd.read_parquet(hurbinfo_filepath)  
        else:
            print(f'There is no file : hurbinfo_{self.lastsunday_str}.parquet')

    def convexhull(self):
        convexhull_path = f'{self.preprocessed_path}/convexhull_{self.lastsunday_str}.parquet'

        if not os.path.isfile(convexhull_path):
            # 결과를 저장할 빈 DataFrame 초기화
            self.convexhull_df = pd.DataFrame(columns=['ord_date_ymd', 'br_code', 'area_in_kilometers', 'polygon'])
            min_size = self.allpoints.groupby(['ord_date_ymd', 'cth_br_code']).size()
            valid_hurbs = min_size[min_size > 3].index

            rows = []

            for ord_date_ymd, code in tqdm(valid_hurbs, leave=False, dynamic_ncols=True):
                points_df = self.allpoints[(self.allpoints['ord_date_ymd'] == ord_date_ymd) & (self.allpoints['cth_br_code'] == code)]
                points = points_df[['latitude', 'longitude']].values

                polygon = MultiPoint(points).convex_hull  # Convex Hull 생성
                transformed_polygon = transform_to_meter(polygon)  # 좌표계 변환
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
                    'area_in_kilometers': area_in_meters,
                    'polygon': polygon_coords
                })

            # 결과 DataFrame에 행 추가
            self.convexhull_df = pd.concat([self.convexhull_df, pd.DataFrame(rows)], ignore_index=True)
            self.convexhull_df.to_parquet(convexhull_path, index=False)
            print(f'File saved : convexhull_{self.lastsunday_str}.parquet')
        else:
            self.convexhull_df = pd.read_parquet(convexhull_path)
            print(f'File already exists : convexhull_{self.lastsunday_str}.parquet')

    def merge(self):
        merged_df = pd.merge(self.hurbinfo_df, self.convexhull_df, how='left', left_on=['ord_date_ymd', 'cth_br_code'], right_on=['ord_date_ymd', 'br_code'])
        merged_df['density_index'] = (merged_df['total_count'] * merged_df['area_in_kilometers']) / (merged_df['valid_worker_count'])
        
        file_name = f'result_{self.lastsunday_str}.parquet'
        merged_df.to_parquet(os.path.join(self.result_path, file_name), index=False)
    
    def __call__(self):
        self.data_load()
        self.convexhull()
        self.merge()


# In[53]:


def path_class(ymd):
    file_class = config.path_class(ymd)
    return file_class

# 데이터 로드 Class를 선언하고, 실행 함수
def main(file_class):    
    run_class = create_convexhull(file_class)
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

