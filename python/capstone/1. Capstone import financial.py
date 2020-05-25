# -*- coding: utf-8 -*-
"""
Created on Sun Mar  1 12:30:27 2020

@author: Stephen Sigrist
"""
import os
os.chdir("..")


import pandas as pd
import yfinance as yf

#make dataframe of tickers to gather data about
#tickers_data = pd.read_csv("input files\\equity tickers.csv")
tickers_data = pd.read_csv("input files\\capstone\\capstone_constituents.csv")

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
    
master_finance_df.to_csv("constructed\\capstone\\capstone_equity_ticker_daily.csv", sep=',')



