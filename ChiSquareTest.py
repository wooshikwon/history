#!/usr/bin/env python
# coding: utf-8

# In[2]:


import pandas as pd
import numpy as np
from scipy import stats
import seaborn as sns
import matplotlib.pyplot as plt


# In[23]:


class ChiSquareTest:
    def __init__(self, df):
        self.df = df

    def goodness_of_fit_test(self, expected_counts):
        results = []

        # 관측 빈도 계산
        observed_counts = self.df['value'].value_counts().sort_index()
        
        # 기대 빈도와 관측 빈도의 길이 일치 확인
        if len(observed_counts) != len(expected_counts):
            raise ValueError("The length of observed counts and expected counts must be the same.")
        
        results.append("<Goodness of Fit Test>\n----------")

        # 카이제곱 통계량 계산
        chi2_stat, chi2_pvalue = stats.chisquare(f_obs=observed_counts, f_exp=expected_counts)
        
        # 결과 추가
        results.append(f"Observed counts: {observed_counts.tolist()}")
        results.append(f"Expected counts: {expected_counts}")
        results.append(f"----------\nResult (Chi-Square Goodness of Fit Test) - Chi2 Statistic: {chi2_stat:.4f}, p-value: {chi2_pvalue:.4f}\n")

        # 결과 출력
        for result in results:
            print(result)
        
        return chi2_stat, chi2_pvalue

    def independence_test(self):
        results = []

        # count 열이 있는지 여부에 따라 교차표 생성 방식 변경
        if 'count' in self.df.columns:
            crosstab = pd.crosstab(self.df['group'], self.df['value'], values=self.df['count'], aggfunc='sum').fillna(0)
        else:
            crosstab = pd.crosstab(self.df['group'], self.df['value'])

        # Title
        results.append("<Independence Test>\n----------")
        
        # 기대 빈도 계산
        chi2_stat, chi2_pvalue, dof, expected = stats.chi2_contingency(crosstab)

        # 기대 빈도가 5 미만인 셀 확인
        if np.any(expected < 5):
            # 기대 빈도가 5 미만인 경우 피셔의 정확 검정 사용
            results.append(expected)
            if crosstab.shape == (2, 2):  # 피셔의 정확 검정은 2x2 표에서만 사용 가능
                fisher_stat, fisher_pvalue = stats.fisher_exact(crosstab)
                results.append(f"----------\nPrior Test - f<5 in at least one cell\nResult (Fisher's Exact Test) - Statistic: {fisher_stat:.4f}, p-value: {fisher_pvalue:.4f}\n")
                statistic = fisher_stat
                pvalue = fisher_pvalue

            else:
                results.append("Fisher's Exact Test is not applicable for tables larger than 2x2.")
        else:
            # 기대 빈도가 모두 5 이상인 경우 카이제곱 검정 사용
            results.append(expected)
            results.append(f"----------\nPrior Test - f>=5 in all cells\nResult (Chi-Square Test) - Chi2 Statistic: {chi2_stat:.4f}, p-value: {chi2_pvalue:.4f}\n")
            statistic = chi2_stat
            pvalue = chi2_pvalue

        # 결과 출력
        for result in results:
            print(result)
        
        return statistic, pvalue

    def bar_plot(self, title=None):
        # group 컬럼이 존재하는지 확인
        if 'group' in self.df.columns:
            # 막대 그래프
            fig, ax = plt.subplots(figsize=(8, 6))
            sns.countplot(x='group', hue='value', data=self.df, ax=ax)
        else:
            raise ValueError("The dataframe must contain a 'group' column.")
        
        # 제목
        if title:
            plt.title(title)
        
        plt.show()


# In[24]:

# 예시 데이터
'''
data1 = {
    'group': ['A', 'A', 'A', 'A', 'A', 'A', 'A', 'A', 'A', 'A', 'A', 'A', 'A', 'A', 'B', 'B', 'B', 'B', 'B', 'B', 'B', 'B', 'B', 'B', 'B', 'B', 'B', 'B', 'B', 'B'],
    'value': ['yes', 'no', 'yes', 'no', 'yes', 'no', 'yes', 'no', 'yes', 'no', 'no', 'yes', 'no', 'yes', 'no', 'no', 'yes', 'no', 'yes', 'no', 'no', 'yes', 'no', 'yes', 'no', 'no', 'yes', 'no', 'yes', 'no']
}

data2 = {
    'group': ['이번달', '이번달', '지난달', '지난달'],
    'value': ['회사판매', '시장전체', '회사판매', '시장전체'],
    'count': [257, 1200, 242, 1250]
}

df = pd.DataFrame(data1)

chi_square_test = ChiSquareTest(df)

statistic, pvalue = chi_square_test.independence_test()
chi_square_test.bar_plot()

df2 = pd.DataFrame(data2)

chi_square_test = ChiSquareTest(df2)

statistic, pvalue = chi_square_test.independence_test()
chi_square_test.bar_plot()


# 예시 데이터3
df = pd.DataFrame({
    'group': ['A']*100,
    'value': np.random.choice([1, 2, 3, 4], size=100, p=[0.2, 0.3, 0.3, 0.2])
})

# 기대 빈도 정의 (임의의 예시로 전체 100개의 데이터에 대한 기대 비율을 정의)
expected_counts = [20, 30, 30, 20]

# 테스트 실행
test = ChiSquareTest(df)
chi2_stat, chi2_pvalue = test.goodness_of_fit_test(expected_counts)
test.bar_plot()
'''