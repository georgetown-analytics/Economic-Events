# -*- coding: utf-8 -*-
"""
Created on Sun Mar  1 12:30:27 2020

@author: Stephen Sigrist
"""
import os
os.chdir("..")


import pandas as pd
import yfinance as yf
import numpy as np 
import statsmodels.api as sm

#make dataframe of tickers to gather data about
#tickers_data = pd.read_csv("input files\\equity tickers.csv")
tickers_data = pd.read_csv("input files\\capstone\\big ticker list.csv")
#tickers_data=tickers_data[0:21]
tickers_data=tickers_data.reset_index(drop=True)



#make blank dataframe to fill in with financial data with yfinance
master_finance_df= pd.DataFrame(columns=['date', 'price', 'ticker'])

for i in range(len(tickers_data)):
    temp_tik=tickers_data['ticker'][i]
    print("Begin "+temp_tik)
    temp_df=yf.download(temp_tik, start='2010-01-01', end='2020-12-31', progress=False)
    temp_df['date'] = temp_df.index
    temp_df['price']=temp_df['Close']
    temp_df=temp_df[['date', 'price']]
    temp_df['ticker']=temp_tik
    master_finance_df=master_finance_df.append(temp_df)
    print("End "+temp_tik)
    
master_finance_df= master_finance_df.rename( \
columns={'date': 'datetime'})
master_finance_df['date']=master_finance_df['datetime'].dt.date
master_finance_df.date=pd.to_datetime(master_finance_df.date)

sp500tr_df=pd.read_csv("input files\\SP500TR.csv")
sp500tr_df.date=pd.to_datetime(sp500tr_df.date)

master_finance_df=pd.merge(master_finance_df, sp500tr_df, left_on='date', right_on='date', \
validate='many_to_one')
    
master_finance_df.to_csv("constructed\\capstone\\big_capstone_equity_ticker_daily.csv", sep=',')

#rolling regression for tickers
#to be used to get daily residual for each observation given past 100 obs and sp500
def roll_reg(x, k):
    x.sort_values(by=['date'])
    temp_df_100=x.iloc[k-100:k]
    temp_df_pred_row=x.iloc[k:k+1]
    results= sm.OLS(temp_df_100['ln_return_price'], sm.add_constant(temp_df_100[['ln_return_index']])).fit()
    
    q=float(temp_df_pred_row['ln_return_index'])
    temp_pred =  results.predict([1,q])
    rolling_resid_return=float(temp_df_pred_row.iloc[0,4])-float(temp_pred)
    return rolling_resid_return


master_finance_df= pd.read_csv("constructed\\capstone\\big_capstone_equity_ticker_daily.csv")
master_finance_df= master_finance_df.loc[:, ~master_finance_df.columns.str.contains('^Unnamed')]
master_finance_df.dtypes
master_finance_df=master_finance_df.sort_values(by=['ticker', 'date'])
master_finance_df=master_finance_df.reset_index(drop=True)

stack_df= pd.DataFrame(columns=['ticker', 'date', 'ln_return_price', \
'ln_return_index'])                      
for x in master_finance_df.ticker.unique():
    temp_df=master_finance_df[master_finance_df.ticker ==x]
    temp_df=temp_df.reset_index(drop=True)
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
    temp_df=temp_df.loc[~((temp_df['ln_return_index'] == 0) & (temp_df['ln_return_price'] == 0)),:]
    for p in range(100, len(temp_df)-100):
        #print(p)
        temp_resid=roll_reg(temp_df, p)
        temp_df.iloc[p,6]=temp_resid
    temp_df=temp_df[['ticker','date','ln_return_price', 'ln_return_index', 'roll_resid']]  
    stack_df=stack_df.append(temp_df)
    
stack_df.to_csv("constructed\\big_stack_backup.csv", sep=',')


