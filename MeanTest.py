#!/usr/bin/env python
# coding: utf-8

# In[3]:


import pandas as pd
import numpy as np
from scipy import stats

import seaborn as sns
import matplotlib.pyplot as plt

import warnings
warnings.filterwarnings(action='ignore')


# In[9]:


class meantest:
    def __init__(self, df):
        self.df = df.dropna()

    # 단일표본 검정
    def single_sample_test(self, population_mean):
        columns = list(self.df.columns)

        # df 구조 검사
        if len(columns) != 1 or columns[0] != 'value':
            raise ValueError("The 'value' column is required")

        results = []

        # Title
        results.append("<Single Sample Test>")
        results.append(f"mean({self.df['value'].mean().round(2)}) - population mean({population_mean})\n----------")

        # 정규성 검정 (Shapiro-Wilk Test)
        shapiro_test = stats.shapiro(self.df['value'])
        results.append(f"Step1(Shapiro-Wilk) - Statistic: {shapiro_test.statistic:.4f}, p-value: {shapiro_test.pvalue:.4f}")
        
        if (shapiro_test.pvalue < 0.05) and (len(self.df['value']) < 30):
            # 정규성 검정을 만족하지 못한 경우
            wilcoxon_test = stats.wilcoxon(self.df['value'] - population_mean)
            results.append(f"----------\nPrior Test - Normality X\nResult(Wilcoxon signed-rank test) - Statistic: {wilcoxon_test.statistic:.4f}, p-value: {wilcoxon_test.pvalue:.4f}\n")
            statistic = wilcoxon_test.statistic
            pvalue = wilcoxon_test.pvalue
        else:
            # 정규성 검정을 만족한 경우
            t_test = stats.ttest_1samp(self.df['value'], population_mean)
            results.append(f"----------\nPrior Test - Normality O OR n>= 30\nResult(Single sample t-test) - Statistic: {t_test.statistic:.4f}, p-value: {t_test.pvalue:.4f}\n")
            statistic = t_test.statistic
            pvalue = t_test.pvalue

        for result in results:
            print(result)
        
        return statistic, pvalue

    # 대응표본 검정
    def paired_samples_test(self):
        columns = self.df.columns

        # df 구조 검사
        if len(columns) != 2 or set(columns) != {'before', 'after'}:
            raise ValueError("The 'before' and 'after' columns are required")
        
        results = []

        # Title
        results.append("<Paired Sample Test>")
        results.append(f"before({self.df['before'].mean().round(2)}) - after({self.df['after'].mean().round(2)})\n----------")
        
        # 정규성 검정 (Shapiro-Wilk Test)
        shapiro_group1 = stats.shapiro(self.df['before'])
        shapiro_group2 = stats.shapiro(self.df['after'])
        
        results.append(f"Step1(Shapiro-Wilk for before) - Statistic: {shapiro_group1.statistic:.4f}, p-value: {shapiro_group1.pvalue:.4f}")
        results.append(f"Step1(Shapiro-Wilk for after) - Statistic: {shapiro_group2.statistic:.4f}, p-value: {shapiro_group2.pvalue:.4f}")
        
        if (shapiro_group1.pvalue < 0.05 or shapiro_group2.pvalue < 0.05) and (len(self.df) < 30):
            # 정규성 검정을 만족하지 못한 경우
            wilcoxon_test = stats.wilcoxon(self.df['before'], self.df['after'])
            results.append(f"----------\nPrior Test - Normality X\nResult(Wilcoxon signed-rank test) - Statistic: {wilcoxon_test.statistic:.4f}, p-value: {wilcoxon_test.pvalue:.4f}\n")
            statistic = wilcoxon_test.statistic
            pvalue = wilcoxon_test.pvalue
        else:
            # 정규성 검정을 만족한 경우
            paired_t_test = stats.ttest_rel(self.df['before'], self.df['after'])
            results.append(f"----------\nPrior Test - Normality O OR n>=30\nResult(Paired sample t-test) - Statistic: {paired_t_test.statistic:.4f}, p-value: {paired_t_test.pvalue:.4f}\n")
            statistic = paired_t_test.statistic
            pvalue = paired_t_test.pvalue
        
        for result in results:
            print(result)
        
        return statistic, pvalue
    
    # 독립표본 검정
    def independent_samples_test(self):
        columns = self.df.columns

        # df 구조 검사
        if len(columns) != 2 or set(columns) != {'group', 'value'}:
            raise ValueError("The 'group' and 'value' columns are required")

        # 그룹 레벨이 2개 뿐이어야 함
        if self.df['group'].nunique() != 2:
            raise ValueError("Single sample test require exactly two levels.")
        
        group1 = self.df['group'].unique()[0]
        group2 = self.df['group'].unique()[1]

        group1_value = self.df[self.df['group'] == group1]['value'].reset_index(drop=True)
        group2_value = self.df[self.df['group'] == group2]['value'].reset_index(drop=True)

        results = []

        # Title
        results.append("<Independent Samples Test>")
        results.append(f"{group1}({group1_value.mean().round(2)}) - {group2}({group2_value.mean().round(2)})\n----------")

        # 정규성 검정 (Shapiro-Wilk Test)
        shapiro_group1 = stats.shapiro(group1_value)
        shapiro_group2 = stats.shapiro(group2_value)
        
        results.append(f"Step1(Shapiro-Wilk for {group1}) - Statistic: {shapiro_group1.statistic:.4f}, p-value: {shapiro_group1.pvalue:.4f}")
        results.append(f"Step1(Shapiro-Wilk for {group2}) - Statistic: {shapiro_group2.statistic:.4f}, p-value: {shapiro_group2.pvalue:.4f}")
        
        if (shapiro_group1.pvalue < 0.05 or shapiro_group2.pvalue < 0.05) and (len(group1) < 30 or len(group2) < 30):
            # 정규성 검정을 만족하지 못하고 표본 크기가 30 미만인 경우
            mann_whitney_u_test = stats.mannwhitneyu(group1_value, group2_value)
            results.append(f"----------\nPrior Test - Normality X\nResult(Mann-Whitney U test) - Statistic: {mann_whitney_u_test.statistic:.4f}, p-value: {mann_whitney_u_test.pvalue:.4f}\n")
            statistic = mann_whitney_u_test.statistic
            pvalue = mann_whitney_u_test.pvalue
        else:
            # 정규성 검정을 만족한 경우 또는 표본 크기가 30 이상인 경우
            levene_test = stats.levene(group1_value, group2_value)
            results.append(f"Step2(Levene’s) - Statistic: {levene_test.statistic:.4f}, p-value: {levene_test.pvalue:.4f}")
            
            if levene_test.pvalue < 0.05:
                # 등분산성을 만족하지 못한 경우
                welch_t_test = stats.ttest_ind(group1_value, group2_value, equal_var=False)
                results.append(f"----------\nPrior Test - Normality O OR n>=30 / Equal Variance X\nResult(Welch t-test) - Statistic: {welch_t_test.statistic:.4f}, p-value: {welch_t_test.pvalue:.4f}\n")
                statistic = welch_t_test.statistic
                pvalue = welch_t_test.pvalue
            else:
                # 등분산성을 만족한 경우
                independent_t_test = stats.ttest_ind(group1_value, group2_value, equal_var=True)
                results.append(f"----------\nPrior Test - Normality O OR n>=30 / Equal Variance O\nResult(Independent samples t-test) - Statistic: {independent_t_test.statistic:.4f}, p-value: {independent_t_test.pvalue:.4f}\n")
                statistic = independent_t_test.statistic
                pvalue = independent_t_test.pvalue

        for result in results:
            print(result)
        
        return statistic, pvalue

    def bar_plot(self):
        columns = self.df.columns
        
        if len(columns) == 1 and columns[0] == 'value':
            fig, ax = plt.subplots(figsize=(3, 6))
            plt.title = 'Single Sample Test'
            sns.barplot(x=['Sample'], y=[self.df['value'].mean()], yerr=[self.df['value'].std()], ax=ax)
            ax.set_ylabel('Value')
            ax.set_title('Mean and Standard Deviation of Value')
            plt.show()

        elif len(columns) == 2 and set(columns) == {'before', 'after'}:
            # 각 컬럼의 평균과 표준편차 계산
            mean_values = self.df.mean()
            std_values = self.df.std()

            # 그래프 그리기
            fig, ax = plt.subplots()
            ax.bar(mean_values.index, mean_values.values, yerr=std_values.values, capsize=5)
            ax.set_ylabel('Value')
            ax.set_title('Mean and Standard Deviation of Before and After')
            plt.show()

        elif len(columns) == 2 and set(columns) == {'group', 'value'}:
            # 각 그룹의 평균과 표준편차 계산
            group_stats = self.df.groupby('group')['value'].agg(['mean', 'std']).reset_index()

            # 그래프 그리기
            fig, ax = plt.subplots()
            ax.bar(group_stats['group'], group_stats['mean'], yerr=group_stats['std'], capsize=5)
            ax.set_ylabel('Value')
            ax.set_title('Mean and Standard Deviation of Value by Group')
            plt.show()
        else:
            raise ValueError("single_sample_test require 'value' column\nindependent_samples_test require 'group' & 'value' columns\npaired_samples_test require 'before' & 'after' columns")



# In[12]:

'''
# 예시 데이터
data1 = {
    'group': ['A', 'A', 'A', 'A', 'A', 'B', 'B', 'B', 'B', 'B'],
    'value': [2.3, 3.1, 2.9, 2.6, 2.7, 3.8, 4.0, 3.5, 4.2, 3.7]
}

df1 = pd.DataFrame(data1)

test = meantest(df1)
test.independent_samples_test()
test.bar_plot()

# 예시 데이터프레임 생성
data2 = {
    'before': [5, 7, 8, 6, 9, 5, 10, 6, 7, 8],
    'after': [6, 8, 9, 7, 10, 6, 11, 7, 8, 9]
}

df2 = pd.DataFrame(data2)
test = meantest(df2)
test.paired_samples_test()
test.bar_plot()


# 예시 데이터프레임 생성
data3 = {
    'value': [4.7, 5.1, 5.3, 4.8, 5.2, 4.9, 5.0, 5.4, 4.8, 5.1]
}

df3 = pd.DataFrame(data3)
test = meantest(df3)
test.single_sample_test(5)
test.bar_plot()

'''