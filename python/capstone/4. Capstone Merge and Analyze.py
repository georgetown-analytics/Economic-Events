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
from pandasql import sqldf

#rolling regression for tickers
#to be used to get daily residual for each observation given past 100 obs and sp500
def roll_reg(x, k):
    x.sort_values(by=['date'])
    temp_df_100=x.iloc[k-99:k+1]

    results= sm.OLS(temp_df_100['ln_return_price'], sm.add_constant(temp_df_100[['ln_return_index']])).fit()
    temp_df_100['residuals'] = results.resid
    rolling_resid_return=temp_df_100.iloc[99, 7]
    return rolling_resid_return


master_finance_df= pd.read_csv("constructed\\capstone\\capstone_equity_ticker_daily.csv")
master_finance_df= master_finance_df.loc[:, ~master_finance_df.columns.str.contains('^Unnamed')]
master_finance_df.dtypes
master_finance_df=master_finance_df.sort_values(by=['ticker', 'date'])
master_finance_df=master_finance_df.reset_index(drop=True)

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
    
stack_df.to_csv("constructed\\stack_backup.csv", sep=',')
#stack_df=pd.read_csv("constructed\\stack_backup.csv", sep=',') 
stack_df= stack_df.loc[:, ~stack_df.columns.str.contains('^Unnamed')]
stack_df.dtypes
    
master_finance_df=pd.merge(master_finance_df, stack_df, how='inner', \
on=['date', 'ticker'], validate='one_to_one')
master_finance_df.dtypes

master_finance_df=master_finance_df.sort_values(by=['ticker', 'date'])

master_finance_df['year']=pd.DatetimeIndex(master_finance_df['date']).year
master_finance_df['month']=pd.DatetimeIndex(master_finance_df['date']).month
master_finance_df.to_csv("constructed\\capstone\\master_finance_save.csv", sep=',')
pysqldf = lambda q: sqldf(q, globals())
q  = """
SELECT DISTINCT
ticker, year, month,
AVG(roll_resid) as mthly_ave_resid
FROM
master_finance_df
GROUP BY
ticker, year, month
ORDER BY
ticker, year, month
"""
mthly_finance= pysqldf(q)
mthly_finance=mthly_finance[mthly_finance['mthly_ave_resid']!=0]



#merge on event data:
#SEC EVENTS
master_sec_df=pd.read_csv("constructed\\capstone\\capstone_tabulated_sec.csv")
master_sec_df= master_sec_df.loc[:, ~master_sec_df.columns.str.contains('^Unnamed')]
master_sec_df=master_sec_df.drop_duplicates(subset=["date","ticker"], keep="first")
master_sec_df=master_sec_df[master_sec_df['date']>'2010-01-01']
master_sec_df['year']=pd.DatetimeIndex(master_sec_df['date']).year
master_sec_df['month']=pd.DatetimeIndex(master_sec_df['date']).month

#aggregate to monthly
pysqldf = lambda q: sqldf(q, globals())
q  = """
SELECT DISTINCT
ticker, year, month,
SUM(poswords) as sec_pos_words,
SUM(negwords) as sec_neg_words,
SUM(daily_filing_count) as mthly_filing_count
FROM
master_sec_df
GROUP BY
ticker, year, month
ORDER BY
ticker, year, month
"""
mthly_sec= pysqldf(q)

#GOOGLE SCRAPE EVENTS
scrape_df=pd.read_csv("constructed\\capstone\\google_scrape_mthly.csv")
scrape_df= scrape_df.loc[:, ~scrape_df.columns.str.contains('^Unnamed')]

all_mthly_df1=pd.merge(mthly_finance, mthly_sec, how='left', \
on=['ticker', 'year', 'month'], validate='one_to_one')

all_mthly_df2=pd.merge(all_mthly_df1, scrape_df, how='left', \
on=['ticker', 'year', 'month'], validate='one_to_one')
    
all_mthly_df2['sec_pos_words'].fillna(0, inplace=True)
all_mthly_df2['sec_neg_words'].fillna(0, inplace=True)
all_mthly_df2['mthly_filing_count'].fillna(0, inplace=True)
all_mthly_df2['gs_poswords'].fillna(0, inplace=True)
all_mthly_df2['gs_negwords'].fillna(0, inplace=True)

all_mthly_df2.to_csv("constructed\\capstone\\combined_mthly_dataset.csv", sep=',')