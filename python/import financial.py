# -*- coding: utf-8 -*-
"""
Created on Sun Mar  1 12:30:27 2020

@author: Stephen Sigrist
"""
import os
os.chdir("..")
print(os.getcwd())

import pandas as pd
import yfinance as yf
import yahoofinancials

tickers_data = pd.read_csv("input files\\equity tickers.csv")

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
    
master_finance_df.to_csv("constructed\\equity_ticker_daily.csv", sep=',')