# -*- coding: utf-8 -*-
"""
Created on Sun Mar 29 14:31:25 2020

@author: Stephen Sigrist
"""
import os
os.chdir("..")


import numpy as np 
import pandas as pd
import statsmodels.api as sm

#rolling regression for tickers
#to be used to get daily residual for each observation given past 100 obs and sp500
def roll_reg(x, k):
    x.sort_values(by=['date'])
    temp_df_100=x.iloc[k-99:k+1]

    results= sm.OLS(temp_df_100['ln_return_price'], sm.add_constant(temp_df_100[['ln_return_index']])).fit()
    temp_df_100['residuals'] = results.resid
    rolling_resid_return=temp_df_100.iloc[99, 4]
    return rolling_resid_return


master_finance_df= pd.read_csv("constructed\\equity_ticker_daily.csv")

#Does the following: calculation ln return price; ln return index; makes daily residuals
#using roll_reg function above
stack_df= pd.DataFrame(columns=['ticker', 'date', 'ln_return_price', \
'ln_return_index'])                      
for x in master_finance_df.ticker.unique():
    temp_df=master_finance_df[master_finance_df.ticker ==x]
    temp_df=temp_df[['price','ticker','date','sp500']]
    temp_df['ln_return_price']=float(0)
    temp_df['ln_return_index']=float(0)
    temp_df['roll_resid']=float(0)
    temp_df.sort_values(by=['date'])
    for i in range(1, len(temp_df)):
        try:
            temp_price_ret=np.log(temp_df.iloc[i][0]/temp_df.iloc[i-1][0])
            temp_index_ret=np.log(temp_df.iloc[i][3]/temp_df.iloc[i-1][3])
            temp_df.iloc[i,4]=temp_price_ret
            temp_df.iloc[i,5]=temp_index_ret
        except:
            temp_df.iloc[i,4]=0
            temp_df.iloc[i,5]=0
    for p in range(100, len(temp_df)-100):
        temp_resid=roll_reg(temp_df, p)
        temp_df.iloc[p,6]=temp_resid
    temp_df=temp_df[['ticker','date','ln_return_price', 'ln_return_index', 'roll_resid']]  
    stack_df=stack_df.append(temp_df)
    

         
master_finance_df=pd.merge(master_finance_df, stack_df, how='left', \
on=['date', 'ticker'], validate='one_to_one')

master_finance_df=master_finance_df.sort_values(by=['ticker', 'date'])

#merge on event data:
master_sec_df=pd.read_csv("constructed\\sec_data_tabulated.csv")
master_sec_df=master_sec_df[['date', 'ticker', 'text_mention_decline', 'text_mention_growth']]
master_sec_df=master_sec_df.drop_duplicates(subset=["date","ticker"], keep="first")


analysis_df=pd.merge(master_finance_df, master_sec_df, how='left', \
on=['date', 'ticker'], validate='one_to_one')
analysis_df['text_mention_decline'].fillna(0, inplace=True)
analysis_df['text_mention_growth'].fillna(0, inplace=True)
analysis_subset_df=analysis_df[analysis_df.roll_resid!=0]

#regress daily residuals on "text mention decline" and "text mention growth"
results=sm.OLS(analysis_subset_df['roll_resid'], \
sm.add_constant(analysis_subset_df[['text_mention_decline', 'text_mention_growth']])).fit()
print(results.summary())

