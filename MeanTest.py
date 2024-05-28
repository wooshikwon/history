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
        self.df = df

    # 단일표본 검정
    def single_sample_test(self, population_mean):
        results = []

        # 그룹 레벨이 1개 뿐이어야 함
        if self.df['group'].nunique() > 1:
            raise ValueError("Single tests require only one group.")

        group = self.df['group'].unique()
        group_value = self.df[self.df['group'] == group]['value'].reset_index(drop=True)

        # Title
        results.append("<Single Sample Test>")
        results.append(f"{group}({group_value.mean().round(2)}) - population mean({population_mean})\n----------")

        # 정규성 검정 (Shapiro-Wilk Test)
        shapiro_test = stats.shapiro(group_value)
        results.append(f"Step1(Shapiro-Wilk) - Statistic: {shapiro_test.statistic:.4f}, p-value: {shapiro_test.pvalue:.4f}")
        
        if (shapiro_test.pvalue < 0.05) and (len(self.df) < 30):
            # 정규성 검정을 만족하지 못한 경우
            wilcoxon_test = stats.wilcoxon(group_value - population_mean)
            results.append(f"----------\nPrior Test - Normality X\nResult(Wilcoxon signed-rank test) - Statistic: {wilcoxon_test.statistic:.4f}, p-value: {wilcoxon_test.pvalue:.4f}\n")
            statistic = wilcoxon_test.statistic
            pvalue = wilcoxon_test.pvalue
        else:
            # 정규성 검정을 만족한 경우
            t_test = stats.ttest_1samp(group_value, population_mean)
            results.append(f"----------\nPrior Test - Normality O OR n>= 30\nResult(Single sample t-test) - Statistic: {t_test.statistic:.4f}, p-value: {t_test.pvalue:.4f}\n")
            statistic = t_test.statistic
            pvalue = t_test.pvalue

        for result in results:
            print(result)
        
        return statistic, pvalue

    # 대응표본 검정
    def paired_samples_test(self):
        results = []

        # 그룹 레벨이 2개 뿐이어야 함
        if self.df['group'].nunique() != 2:
            raise ValueError("Paired Sample tests require two groups.")
        
        group1 = self.df['group'].unique()[0]
        group2 = self.df['group'].unique()[1]

        group1_value = self.df[self.df['group'] == group1]['value'].reset_index(drop=True)
        group2_value = self.df[self.df['group'] == group2]['value'].reset_index(drop=True)
        
        # 두 그룹의 표본 수가 동일해야 함
        if len(group1_value) != len(group2_value):
            raise ValueError("Paired tests require both groups to have the same number of observations.")
        
        # Title
        results.append("<Paired Sample Test>")
        results.append(f"{group1}({group1_value.mean().round(2)}) - {group2}){group2_value.mean().round(2)})\n----------")
        
        # 정규성 검정 (Shapiro-Wilk Test)
        shapiro_group1 = stats.shapiro(group1_value)
        shapiro_group2 = stats.shapiro(group2_value)
        
        results.append(f"Step1(Shapiro-Wilk for {group1}) - Statistic: {shapiro_group1.statistic:.4f}, p-value: {shapiro_group1.pvalue:.4f}")
        results.append(f"Step1(Shapiro-Wilk for {group2}) - Statistic: {shapiro_group2.statistic:.4f}, p-value: {shapiro_group2.pvalue:.4f}")
        
        if (shapiro_group1.pvalue < 0.05 or shapiro_group2.pvalue < 0.05) and (len(group1_value) < 30 or len(group2_value) < 30):
            # 정규성 검정을 만족하지 못한 경우
            wilcoxon_test = stats.wilcoxon(group1_value, group2_value)
            results.append(f"----------\nPrior Test - Normality X\nResult(Wilcoxon signed-rank test) - Statistic: {wilcoxon_test.statistic:.4f}, p-value: {wilcoxon_test.pvalue:.4f}\n")
            statistic = wilcoxon_test.statistic
            pvalue = wilcoxon_test.pvalue
        else:
            # 정규성 검정을 만족한 경우
            paired_t_test = stats.ttest_rel(group1_value, group2_value)
            results.append(f"----------\nPrior Test - Normality O OR n>=30\nResult(Paired sample t-test) - Statistic: {paired_t_test.statistic:.4f}, p-value: {paired_t_test.pvalue:.4f}\n")
            statistic = paired_t_test.statistic
            pvalue = paired_t_test.pvalue
        
        for result in results:
            print(result)
        
        return statistic, pvalue
    
    # 독립표본 검정
    def independent_samples_test(self):
        results = []

        # 그룹 레벨이 2개 뿐이어야 함
        if self.df['group'].nunique() != 2:
            raise ValueError("Single tests require two groups.")
        
        group1 = self.df['group'].unique()[0]
        group2 = self.df['group'].unique()[1]

        group1_value = self.df[self.df['group'] == group1]['value'].reset_index(drop=True)
        group2_value = self.df[self.df['group'] == group2]['value'].reset_index(drop=True)

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

    def bar_plot(self, title=None, estimator=np.mean):
        # group 컬럼이 존재하는지 확인
        if 'group' in self.df.columns:          
            # 막대 그래프
            fig, ax = plt.subplots(figsize=(8, 6))
            sns.barplot(x='group', y='value', data=self.df, estimator=estimator, ci='sd', ax=ax)
        else:
            # group 컬럼이 없는 경우, 단일 그룹으로 처리
            fig, ax = plt.subplots(figsize=(8, 6))
            sns.barplot(x=np.repeat('Sample', len(self.df)), y='value', data=self.df, estimator=estimator, ci='sd', ax=ax)
        
        # 제목
        if title:
            plt.title(title)
        
        plt.show()


# In[12]:

'''
# 예시 데이터
data = {
    'group': ['A', 'A', 'A', 'A', 'A', 'B', 'B', 'B', 'B', 'B'],
    'value': [2.3, 3.1, 2.9, 2.6, 2.7, 3.8, 4.0, 3.5, 4.2, 3.7]
}

df = pd.DataFrame(data)

meantest = MeanTest(df)
results = meantest.independent_samples_test()

for result in results:
    print(result)

meantest.bar_plot()

'''