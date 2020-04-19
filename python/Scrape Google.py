# -*- coding: utf-8 -*-
"""
Created on Thu Apr  9 12:39:58 2020

@author: Stephen Sigrist
"""
import os
os.chdir("..")

import urllib3
import requests
from bs4 import BeautifulSoup
import pandas as pd
import re

# 1: Create Daily Ticker dataframe
#1a: add company name to ticker list
tickers_data = pd.read_csv("input files\\equity tickers.csv")

def get_symbol(symbol):
    url = "http://d.yimg.com/autoc.finance.yahoo.com/autoc?query={}&region=1&lang=en".format(symbol)

    result = requests.get(url).json()

    for x in result['ResultSet']['Result']:
        if x['symbol'] == symbol:
            return x['name']

tickers_data['company_name']=tickers_data.ticker.apply(get_symbol)
tickers_data['company_name']=tickers_data['company_name'].str.replace('[^\w\s]','')
tickers_data['merge_key']=1
tickers_data['company_name']=tickers_data['company_name'].str.upper() 
tickers_data['company_name']=tickers_data['company_name'].str.replace('INCORPORATED', '')
tickers_data['company_name']=tickers_data['company_name'].str.replace('INC', '')
tickers_data['company_name']=tickers_data['company_name'].str.replace('COMPANY', '')
tickers_data['company_name']=tickers_data['company_name'].str.replace('CORPORATION', '')
tickers_data['company_name']=tickers_data['company_name'].str.replace('CORP', '')
tickers_data['name_word_count']=tickers_data['company_name'].str.count(' ') 

#1b: expand to daily
days= pd.date_range(start='1/1/2010',end='1/31/2010', freq='D',name='datetime')
days_df=pd.DataFrame({ 'dt': days })
days_df['date']=days_df['dt'].dt.date
days_df['merge_key']=1
del days_df['dt']
days_df['string_date']=pd.to_datetime(days_df['date']).\
dt.strftime("%Y-%m-%d").replace("NaT", "")
days_df['str_year']=pd.DatetimeIndex(days_df['date']).year.astype(str)
days_df['str_month']=pd.DatetimeIndex(days_df['date']).month.astype(str)
days_df['str_day']=pd.DatetimeIndex(days_df['date']).day.astype(str)
#mask = (days_df['str_day'].str.len==1)
#days_df['str_day']=days_df.loc[mask, 'str_day']=.str.strip().str.replace("A1","Bad")  


long_daily_df=pd.merge(tickers_data, days_df, on='merge_key')
long_daily_df['query']=long_daily_df["ticker"] + " + "+ long_daily_df['company_name']+" on:"+\
long_daily_df["str_year"]+"-"+long_daily_df["str_month"]+"-"+long_daily_df["str_day"]
print(long_daily_df['query'][0])

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) \
Chrome/80.0.3987.163 Safari/537.36"

master_results_df= pd.DataFrame(columns=['query', 'ticker', 'date',\
'str_year', 'str_month', 'str_day','title', 'link'])

for a in range(len(long_daily_df)):
    query =long_daily_df['query'][a]
    print(query)

    URL = f"https://google.com/search?q={query}"
    headers = {"user-agent" : USER_AGENT}
    resp = requests.get(URL, headers=headers)
    x=resp.status_code
    if resp.status_code == 200:
        soup = BeautifulSoup(resp.content, "html.parser")
    
    results = []
    for g in soup.find_all('div', class_='r'):
        anchors = g.find_all('a')
        if anchors:
            link = anchors[0]['href']
            title = g.find('h3').text
            item = {
                "title": title,
                "link": link
                }
        results.append(item)
    temp_results_df=pd.DataFrame(results)
    temp_results_df['query']=query
    temp_results_df['date']=long_daily_df['date'][a]
    temp_results_df['ticker']=long_daily_df['ticker'][a]
    temp_results_df['str_year']=long_daily_df['str_year'][a]
    temp_results_df['str_month']=long_daily_df['str_month'][a]
    temp_results_df['str_day']=long_daily_df['str_day'][a]
    master_results_df=master_results_df.append(temp_results_df)

#Parse link for dates
#master_results_df['link_contains_year']=master_results_df.\
#apply(lambda row: row.str_year in row.link, axis=1)
master_results_df['str_month']=master_results_df['str_month'].str.zfill(2)
master_results_df['str_day']=master_results_df['str_day'].str.zfill(2)
master_results_df['str_yrmon']=master_results_df.str_year+"/"+master_results_df.str_month

master_results_df['link_contains_yrmon']=master_results_df.\
apply(lambda row: row.str_year in row.link, axis=1)

subset_df=master_results_df[master_results_df['link_contains_yrmon']==True]
subset_df=subset_df[['ticker', 'date', 'link_contains_yrmon']]

    
    
