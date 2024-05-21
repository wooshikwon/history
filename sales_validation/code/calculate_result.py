#!/usr/bin/env python
# coding: utf-8

# In[1]:


import config
from packages import *


# In[2]:


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


# In[4]:


class making_report:
    def __init__(self, path_class):
        self.path_class = path_class
        self.raw_path = self.path_class.raw_path
        self.preprocessed_path = self.path_class.preprocessed_path
        self.upload_path = self.path_class.upload_path
        self.ymd = format_date(path_class.ymd)

        self.result_path_ymd = self.path_class.result_path_ymd
        
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
        usecols = ['hq_margin_roadshop', 'hq_taxagencyfee_roadshop', 'hq_margin_b2b', 'hq_taxagencyfee_b2b', 'hq_margin_od', 'hq_affilmgmtfee_monthlyfee']

        df_targetmonth = self.mergeall[self.mergeall['ym'] == self.targetmonth][usecols].sum()
        df_lastmonth = self.mergeall[self.mergeall['ym'] == self.lastmonth][usecols].sum()
        
        # DataFrame 생성 및 결합
        temp = pd.DataFrame({
            'Last Month': df_lastmonth,
            'Target Month': df_targetmonth
        })

        # 변화량 계산
        temp['Change'] = temp['Target Month'] - temp['Last Month']
        temp['Rate of change'] = (temp['Target Month'] - temp['Last Month']) / temp['Last Month']*100

        temp.loc['Total'] = temp.sum()
        temp.loc['Total', 'Rate of change'] = (temp.loc['Total', 'Target Month'] - temp.loc['Total', 'Last Month']) / temp.loc['Total', 'Last Month']*100
        
        # 숫자 포맷 적용
        for col in ['Target Month', 'Last Month', 'Change']:
            temp[col] = temp[col].apply(lambda x: '{:,.0f}'.format(x) if isinstance(x, (int, float)) else x)
        
        for col in ['Rate of change']:
            temp[col] = temp[col].apply(lambda x: '{:.2f}'.format(x) if isinstance(x, (int, float)) else x)

        temp.columns = [f'{self.lastmonth}', f'{self.targetmonth}', '변화량', '변화율']
        temp.index = ['로드샵_콜비', '로드샵_정산대행수수료', 'B2B_콜비', 'B2B_정산대행수수료', '배민/요기배달_선차감', '월정액관리비수수료', '총계'] 

        # 이미지로 저장
        dfi.export(temp, f'{self.result_path_ymd}/{self.ymd}_101.png', max_cols=-1, max_rows=-1)

    # 1-2. 배달시장 전체 및 바로고 M/S
    def result_102(self):
    
        usecols = ['ym', 'market_cnt', 'ordinary_delivery_cnt', 'br_cnt_roadshop', 'br_cnt_b2b']
        
        temp = self.mergeall[usecols]

        df_targetmonth = temp[temp['ym'] == self.targetmonth].sum().loc[['market_cnt', 'ordinary_delivery_cnt', 'br_cnt_roadshop', 'br_cnt_b2b']]
        df_lastmonth = temp[temp['ym'] == self.lastmonth].sum().loc[['market_cnt', 'ordinary_delivery_cnt', 'br_cnt_roadshop', 'br_cnt_b2b']]

        # DataFrame 생성 및 결합
        temp2 = pd.DataFrame({
            'Last Month': df_lastmonth,
            'Target Month': df_targetmonth
        })

        # 전체 합산과 비중 계산
        barogo_sum = (temp2.loc['br_cnt_roadshop'] + temp2.loc['br_cnt_b2b'])
        ms = (temp2.loc['br_cnt_roadshop'] + temp2.loc['br_cnt_b2b']) / temp2.loc['market_cnt']*100

        temp2.loc['barogo_cnt', 'Last Month'] = barogo_sum[0]
        temp2.loc['barogo_cnt', 'Target Month'] = barogo_sum[1]

        temp2.loc['M/S', 'Last Month'] = ms[0]
        temp2.loc['M/S', 'Target Month'] = ms[1]

        temp2['변화량'] = temp2['Target Month'] - temp2['Last Month']
        temp2['변화율'] = (temp2['Target Month'] - temp2['Last Month']) / temp2['Last Month']*100

        temp2.iloc[5,3] = np.nan

        temp2.columns = [f'{self.lastmonth}', f'{self.targetmonth}', '변화량', '변화율']
        temp2.index = ['전체시장_건수', 'OD_건수', '바로고_로드샵건수', '바로고_B2B건수', '바로고_전체건수', '바로고_M/S']

        # 포맷팅 함수 정의
        def format_cells(x, row, col):
            if row == len(temp2) - 1 and col == len(temp2.columns) - 1:  # 맨 마지막 row와 맨 마지막 컬럼
                return f"{x:.0f}"
            else:
                return f"{x:,.2f}"

        # 포맷팅 적용
        df_formatted = temp2.copy()
        for row in range(len(temp2)):
            for col in range(len(temp2.columns)):
                df_formatted.iloc[row, col] = format_cells(temp2.iloc[row, col], row, col)
        
        # 이미지로 저장
        dfi.export(df_formatted, f'{self.result_path_ymd}/{self.ymd}_102.png', max_cols=-1, max_rows=-1)

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
        
        result = temp.sum()[2:]
        result.index = ['시장 영향', 'OD 영향', '신규허브 영향', '이탈허브 영향', '신규B2B 영향', '이탈B2B 영향', '노이즈']
        result = result.to_frame(name='margin')

        for_image = result.copy()
        for_image['margin'] = for_image['margin'].apply(lambda x : '{:,.0f}'.format(x) if isinstance(x, (int, float)) else x)

        dfi.export(for_image, f'{self.result_path_ymd}/{self.ymd}_201.png', max_cols=-1, max_rows=-1)
        return result
    
    def result_201_graph(self, df):
        df['margin'] = df['margin'].astype(float)

        colors = ['#000099', '#006699', '#006400', '#339933', '#FF6633', '#FF9900', '#CCCCCC']
        color_dict = dict(zip(df.index, colors))

        fig, ax = plt.subplots(figsize=(10, 2))

        # Data preparation
        positives = df[df >= 0].squeeze().dropna()
        negatives = df[df < 0].squeeze().dropna()

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
        plt.savefig(f'{self.result_path_ymd}/{self.ymd}_201_graph.png')

    def result_202_data(self):
        market_size_overall = self.market_size.groupby('ym').sum().reset_index()
        hq_profit_overall = self.hq_profit.groupby('ym').sum().reset_index()

        merge = pd.merge(market_size_overall, hq_profit_overall, how='left', on='ym').fillna(0)

        temp = merge[['ym', 'market_cnt', 'hq_overallmargin', 'ordinary_delivery_cnt']]

        temp['market_withoutod'] = temp['market_cnt'] - temp['ordinary_delivery_cnt']

        temp['include_od_index'] = temp['hq_overallmargin'] / temp['market_cnt']
        temp['exclude_od_index'] = temp['hq_overallmargin'] / temp['market_withoutod']

        result = temp[['ym', 'include_od_index', 'exclude_od_index']]
        result['od_influence'] = result['exclude_od_index'] / result['include_od_index'] - 1

        for_image = result.copy()
        for_image.columns = ['연월', 'OD포함시장_수익index', 'OD제외시장_수익index', 'OD영향도']

        dfi.export(for_image, f'{self.result_path_ymd}/{self.ymd}_202.png', max_cols=-1, max_rows=-1)
        return result
    
    def result_202_graph(self, df):
        fig, ax1 = plt.subplots(figsize=(9, 6))

        # 왼쪽 y축 설정
        ax1.plot(df['ym'], df['include_od_index'], label='OD포함시장_수익index', marker='o')
        ax1.plot(df['ym'], df['exclude_od_index'], label='OD제외시장_수익index', marker='o')
        ax1.set_xlabel('연월')
        ax1.set_ylabel('수익Index')
        ax1.set_ylim(0,20) # y축 범위 설정
        ax1.legend(loc='upper left')
        ax1.grid(True)

        # 각 데이터 포인트에 값을 소수점 두 자리로 표기 (왼쪽 y축)
        for i, txt in enumerate(df['include_od_index']):
            ax1.annotate(f"{txt:.2f}", (df['ym'][i], df['include_od_index'][i]), textcoords="offset points", xytext=(0,10), ha='center')
        for i, txt in enumerate(df['exclude_od_index']):
            ax1.annotate(f"{txt:.2f}", (df['ym'][i], df['exclude_od_index'][i]), textcoords="offset points", xytext=(0,10), ha='center')

        # 오른쪽 y축 생성 및 설정
        ax2 = ax1.twinx()
        ax2.plot(df['ym'], df['od_influence'], label='OD영향도', color='green', marker='o')
        ax2.set_ylabel('OD영향도')
        ax2.set_ylim(0, 1)  # 오른쪽 y축 범위 설정
        ax2.legend(loc='upper right')

        # 오른쪽 y축 데이터 포인트에 값을 소수점 두 자리로 표기
        for i, txt in enumerate(df['od_influence']):
            ax2.annotate(f"{txt:.2f}", (df['ym'][i], df['od_influence'][i]), textcoords="offset points", xytext=(0,10), ha='center')

        plt.title('최근 6개월 바로고 수익index 변화 추세')
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig(f'{self.result_path_ymd}/{self.ymd}_202_graph.png')

    def result_203_data(self):
        temp = self.mergeall.groupby('ym')[['newhurbs_hq_profit', 'churnedhurbs_hq_profit']].sum()
        temp['churnedhurbs_hq_profit'] = temp['churnedhurbs_hq_profit']*-1.00
        temp = temp.tail(2)

        for_image = temp.copy()
        for_image.columns = ['신규허브_본사수익마진', '이탈허브_본사수익마진']
        for_image.index.name = '연월'

        dfi.export(for_image, f'{self.result_path_ymd}/{self.ymd}_203.png', max_cols=-1, max_rows=-1)
        return temp

    def result_203_graph(self, df):
        # 그래프 그리기
        fig, ax = plt.subplots()

        # newhurbs_hq_profit은 양의 막대로 그리기
        bars1 = ax.bar(df.index, df['newhurbs_hq_profit'], color='blue', label='신규허브_본사수익마진')
        # churnedhurbs_hq_profit은 음의 막대로 그리기
        bars2 = ax.bar(df.index, df['churnedhurbs_hq_profit'], color='red', label='이탈/휴면허브_본사수익마진')

        ax.axhline(0, color='gray', linewidth=0.8)  # y=0의 가운데 가로선

        # 막대 안에 값 표시 (하얀색 글씨)
        for bar in bars1:
            yval = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2, yval * 0.5, f'{int(yval):,}', va='center', ha='center', color='white')  # 양의 막대 내부에 텍스트

        for bar in bars2:
            yval = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2, yval * 0.5, f'{int(-yval):,}', va='center', ha='center', color='white')  # 음의 막대 내부에 텍스트

        plt.ylabel('본사수익마진')
        plt.title('전월과 당월, 신규-이탈/휴면 허브로 인한 본사수익마진 비교')
        plt.legend()
        plt.tight_layout()
        plt.savefig(f'{self.result_path_ymd}/{self.ymd}_203_graph.png')
    
    def result_204_data(self):
        temp = self.mergeall.groupby('ym')[['newb2bstores_hq_profit', 'churnedb2bstores_hq_profit']].sum()
        temp['churnedb2bstores_hq_profit'] = temp['churnedb2bstores_hq_profit']*-1.00
        temp = temp.tail(2)

        for_image = temp.copy()
        for_image.columns = ['신규B2B상점_본사수익마진', '이탈/휴면B2B상점_본사수익마진']
        for_image.index.name = '연월'

        dfi.export(for_image, f'{self.result_path_ymd}/{self.ymd}_204.png', max_cols=-1, max_rows=-1)
        return temp
    
    def result_204_graph(self, df):
        # 그래프 그리기
        fig, ax = plt.subplots()

        # newhurbs_hq_profit은 양의 막대로 그리기
        bars1 = ax.bar(df.index, df['newb2bstores_hq_profit'], color='blue', label='신규B2B상점_본사수익마진')
        # churnedhurbs_hq_profit은 음의 막대로 그리기
        bars2 = ax.bar(df.index, df['churnedb2bstores_hq_profit'], color='red', label='이탈/휴면B2B상점_본사수익마진')

        ax.axhline(0, color='gray', linewidth=0.8)  # y=0의 가운데 가로선

        # 막대 안에 값 표시 (하얀색 글씨)
        for bar in bars1:
            yval = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2, yval * 0.5, f'{int(yval):,}', va='center', ha='center', color='white')  # 양의 막대 내부에 텍스트

        for bar in bars2:
            yval = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2, yval * 0.5, f'{int(-yval):,}', va='center', ha='center', color='white')  # 음의 막대 내부에 텍스트

        plt.ylabel('본사수익마진')
        plt.title('전월과 당월, 신규-이탈/휴면 B2B상점으로 인한 본사수익마진 비교')
        plt.legend()
        plt.tight_layout()
        plt.savefig(f'{self.result_path_ymd}/{self.ymd}_204_graph.png')

    def result_301(self):
        temp = self.mergeall.groupby(['ym', 'team'])['hq_overallmargin'].sum().reset_index().round(2)

        # 마지막 'ym' 값의 'hq_overallmargin'을 기준으로 팀별 정렬을 위한 데이터 프레임 생성
        latest_margins = temp.sort_values(by='ym').groupby('team').last().reset_index()
        latest_margins = latest_margins.sort_values(by='hq_overallmargin', ascending=False)

        # 플롯 생성
        plt.figure(figsize=(10, 6))  # 그래프 크기 설정

        # 정렬된 팀 순서로 플롯
        colors = ['b', 'g', 'r', 'c', 'm', 'y']  # 팀별 색상 (색상 수 조정 필요)
        for i, team in enumerate(latest_margins['team']):
            team_data = temp[temp['team'] == team]
            plt.plot(team_data['ym'], team_data['hq_overallmargin'], marker='o', color=colors[i % len(colors)], label=f'{team}')

        # 그래프 꾸미기
        plt.title('지난 6개월 팀별 본사수익 변화 추세')
        plt.xlabel('연월')
        plt.ylabel('본사수익')
        plt.xticks(rotation=45)  # x축 라벨 회전
        plt.legend()  # 범례 표시
        plt.grid(True)  # 그리드 표시

        # 그래프 표시
        plt.tight_layout()  # 레이아웃 조정
        plt.savefig(f'{self.result_path_ymd}/{self.ymd}_301.png')

    def result_302(self):
        temp = self.mergeall.groupby(['ym', 'team'])[['hq_margin_roadshop', 'hq_margin_b2b', 'hq_margin_od']].sum()
        temp.columns = ['로드샵 수익변화', 'B2B 수익변화', '배민/요기배달 수익변화']

        latest_two_months = sorted(temp.index.get_level_values('ym').unique(), reverse=True)[:2]

        # 가장 최근 달과 전월 데이터 필터링
        latest_month_data = temp.loc[(latest_two_months[0], slice(None)),:]
        previous_month_data = temp.loc[(latest_two_months[1], slice(None)),:]

        latest_month_data = latest_month_data.reset_index(level='ym').iloc[:,1:4]
        previous_month_data = previous_month_data.reset_index(level='ym').iloc[:,1:4]

        # 변화율 계산: ((가장 최근 달 - 전월) / 전월) * 100
        change_rate = (latest_month_data - previous_month_data)

        # 히트맵 생성
        plt.figure(figsize=(10, 6))
        sns.heatmap(change_rate, annot=True, cmap='coolwarm', fmt=".1f", linewidths=.5)
        plt.title('전월 대비 팀별 로드샵, B2B, 배민/요기배달 본사수익 변화량')

        plt.savefig(f'{self.result_path_ymd}/{self.ymd}_302.png')
    
    def result_303(self):
        temp = self.mergeall.groupby(['ym', 'team'])[['hq_overallmargin', 'market_cnt', 'ordinary_delivery_cnt']].sum()
        temp['market_cnt_withoutod'] = temp['market_cnt'] - temp['ordinary_delivery_cnt']

        temp['include_od_index'] = temp['hq_overallmargin'] / temp['market_cnt']
        temp['exclude_od_index'] = temp['hq_overallmargin'] / temp['market_cnt_withoutod']

        result_dict = {}

        for i in temp.index.get_level_values('team').unique():

            index = temp.loc[(slice(None),f'{i}'),:][['include_od_index', 'exclude_od_index']]
            index['od_influence'] = (index['exclude_od_index'] / index['include_od_index']) - 1

            for_image = index.copy()
            for_image.columns = ['OD포함시장_수익index', 'OD제외시장_수익index', 'OD영향도']
            
            # 각 컬럼에 대한 변화율 계산
            change_rate_OD포함시장 = round(((for_image.iloc[-1, 0] - for_image.iloc[0, 0]) / for_image.iloc[0, 0]) * 100, 2)
            change_rate_OD제외시장 = round(((for_image.iloc[-1, 1] - for_image.iloc[0, 1]) / for_image.iloc[0, 1]) * 100, 2)
            change_rate_OD영향도 = round(((for_image.iloc[-1, 2] - for_image.iloc[0, 2]) / for_image.iloc[0, 2]) * 100, 2)

            # 새로운 row 추가
            new_row = pd.DataFrame({
                'OD포함시장_수익index': [change_rate_OD포함시장],
                'OD제외시장_수익index': [change_rate_OD제외시장],
                'OD영향도': [change_rate_OD영향도]
            }, index=[('6개월간', '변화율(%)')])

            # 새로운 row를 멀티인덱스로 설정
            new_row.index = pd.MultiIndex.from_tuples(new_row.index, names=['ym', 'team'])

            # 데이터프레임에 row 추가
            for_image = pd.concat([for_image, new_row])
            
            # result_dict[f'{i}'] = index
            dfi.export(for_image, f'{self.result_path_ymd}/{self.ymd}_303_{i}.png', max_cols=-1, max_rows=-1)

        return temp

    def result_304(self, df):
        usecols = ['team', 'area_depth2', 'market_cnt', 'hq_overallmargin', 'ordinary_delivery_cnt', 'barogo_cnt', 'newhurbs_hq_profit', 'churnedhurbs_hq_profit', 'newb2bstores_hq_profit', 'churnedb2bstores_hq_profit']

        df_targetmonth = self.mergeall[self.mergeall['ym'] == self.targetmonth][usecols].groupby(['team']).sum().reset_index()
        df_lastmonth = self.mergeall[self.mergeall['ym'] == self.lastmonth][usecols].groupby(['team']).sum().reset_index()

        df_lastmonth['ms'] = df_lastmonth['barogo_cnt'] / df_lastmonth['market_cnt']
        df_lastmonth['hq_profit_percnt'] = df_lastmonth['hq_overallmargin'] / df_lastmonth['barogo_cnt']

        lastmonth_temp = df_lastmonth[['team', 'market_cnt', 'ordinary_delivery_cnt', 'ms', 'hq_profit_percnt', 'hq_overallmargin']]
        lastmonth_temp.columns = ['team', 'lastmonth_market_cnt', 'lastmonth_ordinary_delivery_cnt', 'lastmonth_ms', 'lastmonth_hq_profit_percnt', 'lastmonth_hq_overallmargin']

        targetmonth_temp = df_targetmonth.groupby(['team']).sum().reset_index()

        temp = pd.merge(targetmonth_temp, lastmonth_temp, how='left', on='team')

        temp['market_influence'] = (temp['market_cnt'] - temp['lastmonth_market_cnt'])*temp['lastmonth_ms']*temp['lastmonth_hq_profit_percnt']
        temp['od_influence'] = (temp['ordinary_delivery_cnt'] - temp['lastmonth_ordinary_delivery_cnt'])*temp['lastmonth_ms']*temp['lastmonth_hq_profit_percnt']*-1.0

        temp['hq_profit_diff'] = temp['hq_overallmargin'] - temp['lastmonth_hq_overallmargin']

        temp = temp[['team', 'hq_profit_diff', 'market_influence', 'od_influence', 'newhurbs_hq_profit','churnedhurbs_hq_profit', 'newb2bstores_hq_profit', 'churnedb2bstores_hq_profit']]

        temp['churnedhurbs_hq_profit'] = temp['churnedhurbs_hq_profit']*-1.00
        temp['churnedb2bstores_hq_profit'] = temp['churnedb2bstores_hq_profit']*-1.00
        temp['noise'] = temp['hq_profit_diff'] - (temp['market_influence'] + temp['od_influence'] + temp['newhurbs_hq_profit'] + temp['churnedhurbs_hq_profit'] + temp['newb2bstores_hq_profit'] + temp['churnedb2bstores_hq_profit'])

        temp = temp.fillna(0)

        for num, team in enumerate(df.index.get_level_values('team').unique()):

            for_graph = temp[temp['team'] == f'{team}'].iloc[:,2:]
            for_graph.columns = ['시장 영향', 'OD 영향', '신규허브 영향', '이탈허브 영향', '신규B2B 영향', '이탈B2B 영향', '노이즈']

            for_graph = for_graph.T.rename(columns={num:'margin'})
            for_graph['margin'] = for_graph['margin'].astype(float)

            colors = ['#000099', '#006699', '#006400', '#339933', '#FF6633', '#FF9900', '#CCCCCC']
            color_dict = dict(zip(for_graph.index, colors))

            fig, ax = plt.subplots(figsize=(10, 2))

            # Data preparation
            positives = for_graph[for_graph >= 0].squeeze().dropna()
            negatives = for_graph[for_graph < 0].squeeze().dropna()

            # Initialize an empty list to track which labels have been added to the legend
            added_labels = []

            # Drawing bars for negatives and positives
            for data, label_prefix in [(negatives, '(음수) '), (positives, '(양수)  ')]:
                left = data.cumsum().shift(1, fill_value=0)
                for idx, (col, value) in enumerate(data.items()):
                    if col not in added_labels:
                        ax.barh(y=0, width=value, left=left[idx],
                                color=color_dict[col], edgecolor='black', label=label_prefix + col)
                        added_labels.append(col)
                    else:
                        ax.barh(y=0, width=value, left=left[idx],
                                color=color_dict[col], edgecolor='black')

            # Set chart title and labels
            ax.set_title(f'{team}')
            ax.set_yticks([])
            ax.axvline(x=0, color='gray', linestyle='--', linewidth=1)

            # Set x-axis limits
            max_abs_value = max(abs(negatives.sum()), positives.sum())
            buffer = max_abs_value * 0.1
            ax.set_xlim(-max_abs_value - buffer, max_abs_value + buffer)

            # Display legend
            ax.legend(loc='center left', bbox_to_anchor=(1, 0.5), title='컬럼명')

            plt.tight_layout()  # 레이아웃 조정
            plt.savefig(f'{self.result_path_ymd}/{self.ymd}_304_{team}.png')
            plt.close(fig) 

    def __call__(self):
        self.load_data()

        self.result_101()
        self.result_102()

        df_201 = self.result_201_data()
        self.result_201_graph(df_201)

        df_202 = self.result_202_data()
        self.result_202_graph(df_202)

        df_203 = self.result_203_data()
        self.result_203_graph(df_203)

        df_204 = self.result_204_data()
        self.result_204_graph(df_204)

        self.result_301()
        self.result_302()

        df_303 = self.result_303()
        self.result_304(df_303)


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

