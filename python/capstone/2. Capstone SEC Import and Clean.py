# -*- coding: utf-8 -*-
"""
Created on Sun Mar  1 12:30:27 2020

@author: Stephen Sigrist
"""
import os
os.chdir("..")
import shutil

import pandas as pd
from sec_edgar_downloader import Downloader
import re
import datetime as dt
from past.builtins import execfile
def include(filename):
    if os.path.exists(filename): 
        execfile(filename)
from pandasql import sqldf
        
#words for sentiment analysis
words_df= pd.read_csv("input files\\capstone\\capstone_sentiment.csv")

#make dataframe of tickers to gather data about
tickers_data = pd.read_csv("input files\\capstone\\capstone_constituents.csv", index_col=False)

dl = Downloader("downloaded\\capstone\\SEC")
ctr=0
for i in range(len(tickers_data)):
    print(i)
    for filing_type in dl.supported_filings:
        try:
           #print("point c")
           #dl.get(filing_type, tickers_data['ticker'][i], 1)
           dl.get(filing_type, tickers_data['ticker'][i], 200)
           print("point d")
        except:
            print("An Error Occured While Downloading "+tickers_data['ticker'][i])
    print("Finished Downloading "+tickers_data['ticker'][i])
    ctr=ctr+1

#analyze SEC Documents for Sentiment Words
fmaster_sec_df= pd.DataFrame(columns=['ticker', 'filing_type', 'path', \
'string_datetime'])

for root, dirs, files in os.walk("downloaded\\capstone\\SEC", topdown=False):
    for name in files:
        print(name)
        print(os.path.join(root, name))
        temp_path=os.path.join(root, name)
        temp_ticker=temp_path.split('\\')[4]
        temp_type=temp_path.split('\\')[5]
        
        stemp_df= pd.DataFrame(columns=['ticker', 'filing_type', 'path', \
        'string_datetime'])
        
        try:
            temp_text=open(os.path.join(root, name), "r").read(1000000)
            temp_text_obj=re.search(r'(<ACCEPTANCE-DATETIME>)(.*$)', temp_text, re.M|re.I)
        except:
            temp_text=""
            temp_text_obj=re.search(r'(<ACCEPTANCE-DATETIME>)(.*$)', temp_text, re.M|re.I)
        try:
            temp_text_dt=temp_text_obj.group(2)
        except:
            temp_text_dt=""
            print("No Datetime Found")

        stemp_df =  stemp_df.append({'ticker': temp_ticker, 'filing_type': temp_type, 'path': temp_path, \
        'string_datetime': temp_text_dt}, ignore_index=True)
            
        for k in range(len(words_df)):
            stemp_df[f"w_{k}"]=temp_text.upper().count(words_df['word'][k])
            
        fmaster_sec_df =  fmaster_sec_df.append(stemp_df, ignore_index=True)

        print("SEC Dataset Created")


#variables 3926 and 3927 are datetime and date, respectively
#tosave=fmaster_sec_df
#fmaster_sec_df=tosave
fmaster_sec_df.dtypes
fmaster_sec_df['datetime']=0 
fmaster_sec_df['date']=0
for x in range(len(fmaster_sec_df)):
    try:
        year=int(fmaster_sec_df['string_datetime'][x][0:4])
        month=int(fmaster_sec_df['string_datetime'][x][4:6])
        day=int(fmaster_sec_df['string_datetime'][x][6:8])
        hr=int(fmaster_sec_df['string_datetime'][x][8:10])
        minu=int(fmaster_sec_df['string_datetime'][x][10:12])
        sec=int(fmaster_sec_df['string_datetime'][x][12:14])
        fmaster_sec_df.iloc[x, 3932]=dt.datetime(year, month, day, hr, minu, sec)
        fmaster_sec_df.iloc[x, 3933]=dt.date(year, month, day)
        #print("line {}".format(i))
    except:
        fmaster_sec_df.iloc[x, 3932]=0
        fmaster_sec_df.iloc[x, 3933]=0
        print("No Extractable Date Value")
        
        
tosee=fmaster_sec_df[['string_datetime', 'date']]


#add up positive/negative words
fmaster_sec_df['poswords']=0
fmaster_sec_df['negwords']=0
fmaster_sec_df.dtypes
for k in range(0, 1637):
    #print(f"w_{k}")
    fmaster_sec_df['poswords']=fmaster_sec_df['poswords']+fmaster_sec_df[f"w_{k}"]
    fmaster_sec_df=fmaster_sec_df.drop([f"w_{k}"], axis=1)

for k in range(1637, 3928):
    fmaster_sec_df['negwords']=fmaster_sec_df['negwords']+fmaster_sec_df[f"w_{k}"]
    fmaster_sec_df=fmaster_sec_df.drop([f"w_{k}"], axis=1)

fmaster_sec_df.dtypes


#aggregate to daily observations and output
pysqldf = lambda q: sqldf(q, globals())
q  = """
SELECT DISTINCT
ticker, date, poswords, negwords, COUNT(*) as daily_filing_count
FROM
fmaster_sec_df
GROUP BY
ticker, date
ORDER BY
ticker, date
"""
aggregate_df= pysqldf(q)

aggregate_df.to_csv("constructed\\capstone\\capstone_tabulated_sec.csv", sep=',')


#shutil.rmtree("downloaded\\\capstone\\\SEC", ignore_errors=True)