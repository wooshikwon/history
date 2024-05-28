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
        columns = list(self.df.columns)

        # df 구조 검사
        if len(columns) != 1 or columns[0] != 'value':
            raise ValueError("The 'value' column is required")
        
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
        columns = list(self.df.columns)

        # df 구조 검사
        if len(columns) != 2 or set(columns) != {'group', 'value'}:
            raise ValueError("The 'group' and 'value' columns are required")

        results = []
        crosstab = pd.crosstab(self.df['group'], self.df['value'])

        # Title
        results.append("<Independence Test>\n----------")
        results.append(crosstab)
        
        # 기대 빈도 계산
        chi2_stat, chi2_pvalue, dof, expected = stats.chi2_contingency(crosstab)

        # 기대 빈도가 5 미만인 셀 확인
        if np.any(expected < 5):
            # 기대 빈도가 5 미만인 경우 피셔의 정확 검정 사용
            if crosstab.shape == (2, 2):  # 피셔의 정확 검정은 2x2 표에서만 사용 가능
                _, fisher_pvalue = stats.fisher_exact(crosstab)
                results.append(f"----------\nPrior Test - f<5 in at least one cell\nResult (Fisher's Exact Test) - p-value: {fisher_pvalue:.4f}\n")
                statistic = None
                pvalue = fisher_pvalue

            else:
                results.append("Fisher's Exact Test is not applicable for tables larger than 2x2.")
        else:
            # 기대 빈도가 모두 5 이상인 경우 카이제곱 검정 사용
            results.append(f"----------\nPrior Test - f>=5 in all cells\nResult (Chi-Square Test) - Statistic: {chi2_stat:.4f}, p-value: {chi2_pvalue:.4f}\n")
            statistic = chi2_stat
            pvalue = chi2_pvalue

        # 결과 출력
        for result in results:
            print(result)
        
        return statistic, pvalue
    
    def mcnemar_test(self):
        columns = self.df.columns

        # df 구조 검사
        if len(columns) != 2 or set(columns) != {'before', 'after'}:
            raise ValueError("The 'before' and 'after' columns are required")
        
        results = []
        crosstab = pd.crosstab(self.df['before'], self.df['after'])

        # Title
        results.append("<McNemar Test>\n----------")
        results.append(crosstab)
        
        # 교차표가 2x2인지 확인
        if crosstab.shape == (2, 2):
            b = crosstab.iloc[0, 1]
            c = crosstab.iloc[1, 0]

            # 기대 빈도 계산
            expected_b = (b + c) / 2
            expected_c = (b + c) / 2

            # 기대 빈도가 5 미만인 셀이 있는지 확인
            if expected_b < 5 or expected_c < 5:
                # 피셔의 정확 검정 사용
                _, pvalue = stats.fisher_exact(crosstab)
                results.append(f"----------\nPrior Test - f<5 in at least one cell\nResult (Fisher's Exact Test) - p-value: {pvalue:.4f}\n")
                statistic = None  # 피셔의 정확 검정에서는 검정 통계량이 없음
            else:
                # McNemar 통계량 계산
                mcnemar_stat = (abs(b - c) - 1)**2 / (b + c)
                pvalue = stats.chi2.sf(mcnemar_stat, 1)
                
                results.append(f"----------\nPrior Test - f>=5 in all cells\nResult (McNemar Test) - Statistic: {mcnemar_stat:.4f}, p-value: {pvalue:.4f}\n")
                statistic = mcnemar_stat
        else:
            results.append("McNemar Test is only applicable for 2x2 tables.\n")
            statistic = None
            pvalue = None

        # 결과 출력
        for result in results:
            print(result)
        
        return statistic, pvalue

    def bar_plot(self):
        columns = self.df.columns

        if len(columns) == 1 and columns[0] == 'value':
            # Calculate observed frequencies
            observed_freq = self.df['value'].value_counts().sort_index()

            # Extract unique values
            unique_values = observed_freq.index

            # Calculate expected frequencies (assuming provided probabilities)
            expected_probabilities = [0.2, 0.3, 0.3, 0.2]  # Adjust this part as needed
            expected_freq = np.array(expected_probabilities) * len(self.df)

            fig, ax = plt.subplots(figsize=(10, 6))
            sns.barplot(x=unique_values, y=observed_freq.values, color='blue', alpha=0.6, label='Observed')
            sns.barplot(x=unique_values, y=expected_freq, color='red', alpha=0.6, label='Expected')

            # Plot settings
            ax.set_title('Goodness of Fit Test: Observed vs Expected Frequencies')
            ax.set_xlabel('Value')
            ax.set_ylabel('Frequency')
            ax.legend(title='Legend')

            plt.show()

        elif len(columns) == 2 and set(columns) == {'before', 'after'}:
            # Create crosstab
            crosstab = pd.crosstab(self.df['before'], self.df['after'])

            # Create heatmap
            plt.figure(figsize=(8, 6))
            sns.heatmap(crosstab, annot=True, cmap="YlGnBu", cbar=False)
            plt.title('McNemar Test Contingency Table')
            plt.xlabel('After')
            plt.ylabel('Before')
            plt.show()

        elif len(columns) == 2 and set(columns) == {'group', 'value'}:
            # Create count plot
            plt.figure(figsize=(10, 6))
            sns.countplot(data=self.df, x='group', hue='value')
            plt.title('Count Plot of Values by Group')  # Fixed here
            plt.xlabel('Group')
            plt.ylabel('Count')
            plt.legend(title='Value')
            plt.show()
        else:
            raise ValueError("single_sample_test requires 'value' column\nindependent_samples_test requires 'group' & 'value' columns\npaired_samples_test requires 'before' & 'after' columns")


# In[24]:

# 예시 데이터
'''
data1 = {
    'group': ['A', 'A', 'A', 'A', 'A', 'A', 'A', 'A', 'A', 'A', 'A', 'A', 'A', 'A', 'B', 'B', 'B', 'B', 'B', 'B', 'B', 'B', 'B', 'B', 'B', 'B', 'B', 'B', 'B', 'B'],
    'value': ['yes', 'no', 'yes', 'no', 'yes', 'no', 'yes', 'no', 'yes', 'no', 'no', 'yes', 'no', 'yes', 'no', 'no', 'yes', 'no', 'yes', 'no', 'no', 'yes', 'no', 'yes', 'no', 'no', 'yes', 'no', 'yes', 'no']
}

df = pd.DataFrame(data1)
test = ChiSquareTest(df)
statistic, pvalue = test.independence_test()
test.bar_plot()


data2 = {
    'before': [1, 0, 1, 1, 0, 1, 0, 1, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0],
    'after': [1, 0, 1, 0, 0, 1, 0, 1, 0, 0, 1, 0, 1, 0, 1, 0, 1, 0, 0, 1]
}

df2 = pd.DataFrame(data2)
test = ChiSquareTest(df2)
statistic, pvalue = test.mcnemar_test()
test.bar_plot()


# 예시 데이터3
df3 = pd.DataFrame({
    'value': np.random.choice([1, 2, 3, 4], size=100, p=[0.2, 0.3, 0.3, 0.2])
})

# 기대 빈도 정의 (임의의 예시로 전체 100개의 데이터에 대한 기대 비율을 정의)
expected_counts = [20, 30, 30, 20]

# 테스트 실행
test = ChiSquareTest(df3)
chi2_stat, chi2_pvalue = test.goodness_of_fit_test(expected_counts)
test.bar_plot()
'''