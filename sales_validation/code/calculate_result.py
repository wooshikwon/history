#!/usr/bin/env python
# coding: utf-8

# In[1]:


import config
from packages import *


# In[41]:


import os

import pandas as pd
import numpy as np

from datetime import datetime
from dateutil.relativedelta import relativedelta

import matplotlib.pyplot as plt
plt.rcParams['font.family'] ='AppleGothic'
plt.rcParams['axes.unicode_minus'] =False

import dataframe_image as dfi
import seaborn as sns


# In[3]:


def get_previous_months(date_int):

    date_str = str(date_int)
    date_obj = datetime.strptime(date_str, '%Y%m%d')

    targetmonth = date_obj - relativedelta(months=1)
    lastmonth = date_obj - relativedelta(months=2)

    targetmonth_str = targetmonth.strftime('%Y-%m')
    lastmonth_str = lastmonth.strftime('%Y-%m')

    return targetmonth_str, lastmonth_str


# In[60]:


class making_report:
    def __init__(self, path_class):
        self.path_class = path_class
        self.raw_path = self.path_class.raw_path
        self.preprocessed_path = self.path_class.preprocessed_path
        self.upload_path = self.path_class.upload_path
        self.ymd = format_date(path_class.ymd)
        
        self.targetmonth, self.lastmonth = get_previous_months(path_class.ymd)

    def load_data(self):
        query_list = ['hq_profit', 'market_size', 'new_hurbs', 'churned_hurbs', 'new_b2bstores', 'churned_b2bstores']

        for name in query_list:
            file_path = os.path.join(self.raw_path, f'{name}_{self.ymd}.csv')
            if os.path.isfile(file_path):
                setattr(self, name, pd.read_csv(file_path))
            else:
                pass

        self.team_flag = pd.read_csv(os.path.join(self.preprocessed_path, f'team_flag_{self.ymd}.csv'))
        self.mergeall = pd.read_csv(os.path.join(self.preprocessed_path, f'mergeall_{self.ymd}.csv'))

    # 1-1. 전체 실적 및 바로고 본사 수익
    def result_101(self):
        usecols = ['hq_margin_roadshop', 'hq_taxagencyfee_roadshop', 'hq_margin_b2b', 'hq_taxagencyfee_b2b', 'hq_affilmgmtfee_monthlyfee']

        df_targetmonth = self.mergeall[self.mergeall['ym'] == self.targetmonth][usecols].sum()
        df_lastmonth = self.mergeall[self.mergeall['ym'] == self.lastmonth][usecols].sum()
        
        # DataFrame 생성 및 결합
        temp = pd.DataFrame({
            'Target Month': df_targetmonth,
            'Last Month': df_lastmonth
        })

        # 전체 합산 대비 비중 계산
        temp['Target Month Proportion'] = temp['Target Month'] / temp['Target Month'].sum()
        temp['Last Month Proportion'] = temp['Last Month'] / temp['Last Month'].sum()

        # 변화량 계산
        temp['Change'] = temp['Target Month'] - temp['Last Month']
        temp['Rate of change'] = (temp['Target Month'] - temp['Last Month']) / temp['Last Month']*100

        temp.loc['Total'] = temp.sum()
        temp.loc['Total', 'Rate of change'] = (temp.loc['Total', 'Target Month'] - temp.loc['Total', 'Last Month']) / temp.loc['Total', 'Last Month']*100
        
        # 숫자 포맷 적용
        for col in ['Target Month', 'Last Month', 'Change']:
            temp[col] = temp[col].apply(lambda x: '{:,.0f}'.format(x) if isinstance(x, (int, float)) else x)
        
        for col in ['Target Month Proportion', 'Last Month Proportion', 'Rate of change']:
            temp[col] = temp[col].apply(lambda x: '{:.2f}'.format(x) if isinstance(x, (int, float)) else x)

        # 이미지로 저장
        dfi.export(temp, f'../result/{self.ymd}_101.png', max_cols=-1, max_rows=-1)

    # 1-2. 바로고 콜 수
    def result_102(self):
    
        usecols = ['br_cnt_roadshop', 'br_cnt_b2b']

        df_targetmonth = self.mergeall[self.mergeall['ym'] == self.targetmonth][usecols].sum()
        df_lastmonth = self.mergeall[self.mergeall['ym'] == self.lastmonth][usecols].sum()
        
        # DataFrame 생성 및 결합
        temp = pd.DataFrame({
            'Target Month': df_targetmonth,
            'Last Month': df_lastmonth
        })

        # 전체 합산 대비 비중 계산
        temp['Target Month Proportion'] = temp['Target Month'] / temp['Target Month'].sum()
        temp['Last Month Proportion'] = temp['Last Month'] / temp['Last Month'].sum()

        # 변화량 계산
        temp['Change'] = temp['Target Month'] - temp['Last Month']
        temp['Rate of change'] = (temp['Target Month'] - temp['Last Month']) / temp['Last Month']*100

        temp.loc['Total'] = temp.sum()
        temp.loc['Total', 'Rate of change'] = (temp.loc['Total', 'Target Month'] - temp.loc['Total', 'Last Month']) / temp.loc['Total', 'Last Month']*100

        # 숫자 포맷 적용
        for col in ['Target Month', 'Last Month', 'Change']:
            temp[col] = temp[col].apply(lambda x: '{:,.0f}'.format(x) if isinstance(x, (int, float)) else x)
        
        for col in ['Target Month Proportion', 'Last Month Proportion', 'Rate of change']:
            temp[col] = temp[col].apply(lambda x: '{:.2f}'.format(x) if isinstance(x, (int, float)) else x)
        
        # 이미지로 저장
        dfi.export(temp, f'../result/{self.ymd}_102.png', max_cols=-1, max_rows=-1)

    # 1-3. 배달시장 전체 및 바로고 M/S
    def result_103(self):
    
        usecols = ['ym', 'market_cnt', 'ordinary_delivery_cnt', 'br_cnt_roadshop', 'br_cnt_b2b']
        
        temp = self.mergeall[usecols]
        
        df_targetmonth = temp[temp['ym'] == self.targetmonth].sum().loc[['market_cnt', 'ordinary_delivery_cnt', 'br_cnt_roadshop', 'br_cnt_b2b']]
        df_lastmonth = temp[temp['ym'] == self.lastmonth].sum().loc[['market_cnt', 'ordinary_delivery_cnt', 'br_cnt_roadshop', 'br_cnt_b2b']]
        
        # DataFrame 생성 및 결합
        temp2 = pd.DataFrame({
            'Target Month': df_targetmonth,
            'Last Month': df_lastmonth
        }).T

        # 전체 합산 대비 비중 계산
        temp2['M/S'] = (temp2['br_cnt_roadshop'] + temp2['br_cnt_b2b']) / temp2['market_cnt']*100
        
                # 숫자 포맷 적용
        for col in ['market_cnt', 'ordinary_delivery_cnt', 'br_cnt_roadshop', 'br_cnt_b2b']:
            temp2[col] = temp2[col].apply(lambda x: '{:,.0f}'.format(x) if isinstance(x, (int, float)) else x)
        
        for col in ['M/S']:
            temp2[col] = temp2[col].apply(lambda x: '{:.2f}'.format(x) if isinstance(x, (int, float)) else x)
        
        # 이미지로 저장
        dfi.export(temp2, f'../result/{self.ymd}_103.png', max_cols=-1, max_rows=-1)

    def result_201_data(self):
    
        usecols = ['area_depth1', 'team', 'area_depth2', 'market_cnt', 'hq_overallmargin', 'ordinary_delivery_cnt', 'barogo_cnt', 'newhurbs_hq_profit', 'churnedhurbs_hq_profit', 'newb2bstores_hq_profit', 'churnedb2bstores_hq_profit']

        df_targetmonth = self.mergeall[self.mergeall['ym'] == self.targetmonth][usecols].groupby(['area_depth1']).sum().reset_index()
        df_lastmonth = self.mergeall[self.mergeall['ym'] == self.lastmonth][usecols].groupby(['area_depth1']).sum().reset_index()
        
        df_lastmonth['ms'] = df_lastmonth['barogo_cnt'] / df_lastmonth['market_cnt']
        df_lastmonth['hq_profit_percnt'] = df_lastmonth['hq_overallmargin'] / df_lastmonth['barogo_cnt']

        lastmonth_temp = df_lastmonth[['area_depth1', 'market_cnt', 'ordinary_delivery_cnt', 'ms', 'hq_profit_percnt', 'hq_overallmargin']]
        lastmonth_temp.columns = ['area_depth1', 'lastmonth_market_cnt', 'lastmonth_ordinary_delivery_cnt', 'lastmonth_ms', 'lastmonth_hq_profit_percnt', 'lastmonth_hq_overallmargin']
        
        targetmonth_temp = df_targetmonth.groupby(['area_depth1']).sum().reset_index()
        
        temp = pd.merge(targetmonth_temp, lastmonth_temp, how='left', on='area_depth1')
        
        temp['market_influence'] = (temp['market_cnt'] - temp['lastmonth_market_cnt'])*temp['lastmonth_ms']*temp['lastmonth_hq_profit_percnt']
        temp['od_influence'] = (temp['ordinary_delivery_cnt'] - temp['lastmonth_ordinary_delivery_cnt'])*temp['lastmonth_ms']*temp['lastmonth_hq_profit_percnt']*-1.0

        temp['hq_profit_diff'] = temp['hq_overallmargin'] - temp['lastmonth_hq_overallmargin']
        
        temp = temp[['area_depth1', 'hq_profit_diff', 'market_influence', 'od_influence', 'newhurbs_hq_profit','churnedhurbs_hq_profit', 'newb2bstores_hq_profit', 'churnedb2bstores_hq_profit']]
        
        temp['churnedhurbs_hq_profit'] = temp['churnedhurbs_hq_profit']*-1.00
        temp['churnedb2bstores_hq_profit'] = temp['churnedb2bstores_hq_profit']*-1.00
        temp['noise'] = temp['hq_profit_diff'] - (temp['market_influence'] + temp['od_influence'] + temp['newhurbs_hq_profit'] + temp['churnedhurbs_hq_profit'] + temp['newb2bstores_hq_profit'] + temp['churnedb2bstores_hq_profit'])
        
        self._201 = temp.sum()[2:]
        self._201.index = ['시장 영향', 'OD 영향', '신규허브 영향', '이탈허브 영향', '신규B2B 영향', '이탈B2B 영향', '노이즈']
        
        result = self._201.reset_index(name='margin')
        result['margin'] = result['margin'].apply(lambda x : '{:,.0f}'.format(x) if isinstance(x, (int, float)) else x)

        dfi.export(result, f'../result/{self.ymd}_201.png', max_cols=-1, max_rows=-1)

    def result_201_graph(self):
            # Color mapping
        colors = sns.color_palette('tab10', len(self._201))
        color_dict = dict(zip(self._201.index, colors))

        fig, ax = plt.subplots(figsize=(10, 2))

        # Data preparation
        positives = self._201[self._201 >= 0].sort_values()
        negatives = self._201[self._201 < 0].sort_values()

        # Drawing bars for negatives and positives
        left_negatives = negatives.cumsum().shift(1, fill_value=0)
        for idx, col in enumerate(negatives.index):
            ax.barh(y=0, width=negatives[col], left=left_negatives[idx],
                    color=color_dict[col], edgecolor='black', label=col)

        left_positives = positives.cumsum().shift(1, fill_value=0)
        for idx, col in enumerate(positives.index):
            ax.barh(y=0, width=positives[col], left=left_positives[idx],
                    color=color_dict[col], edgecolor='black', label=col)

        # Set chart title and labels
        ax.set_title('전국')
        ax.set_yticks([])
        ax.axvline(x=0, color='gray', linestyle='--', linewidth=1)

        # Set x-axis limits
        max_abs_value = max(abs(negatives.sum()), positives.sum())
        buffer = max_abs_value * 0.1
        ax.set_xlim(-max_abs_value - buffer, max_abs_value + buffer)

        # Display legend
        handles, labels = ax.get_legend_handles_labels()
        unique_labels = dict(zip(labels, handles))  # Removing duplicates
        ax.legend(unique_labels.values(), unique_labels.keys(), loc='center left', bbox_to_anchor=(1, 0.5), title='컬럼명')

        plt.tight_layout()
        plt.savefig(f'../result/{self.ymd}_201_graph.png')
    
    def __call__(self):
        self.load_data()
        self.result_101()
        self.result_102()
        self.result_103()
        self.result_201_data()
        self.result_201_graph()


# In[ ]:


def path_class(ymd):
    file_class = config.path_class(ymd)
    return file_class

# 본 파일(loaddata.py)의 데이터 로드 Class를 선언하고, 실행 함수
def main(file_class):    
    run_class = making_report(file_class) #brand는 이 스크립트의 특이 추가 인자
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

