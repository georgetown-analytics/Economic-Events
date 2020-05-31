# -*- coding: utf-8 -*-
"""
Created on Sun May 31 14:41:35 2020

@author: Stephen Sigrist
"""

import os
os.chdir("..")


import pandas as pd
import re
import datetime as dt
from pandasql import sqldf
import math

#Create Dataframe of SEC Documents and Extracted Data For Purposes of Sentiment Analysis
REPLACE_NO_SPACE = re.compile("[.;:!\'?,\"()\[\]]")
REPLACE_WITH_SPACE = re.compile("(<br\s*/><br\s*/>)|(\-)|(\/)")


sentiment_df=pd.DataFrame(columns=['ticker', 'path', \
'string_datetime', 'text'])

    
    
for root, dirs, files in os.walk("downloaded\\capstone\\SEC", topdown=False):
    for name in files:
        print(name)
        print(os.path.join(root, name))
        
        temp_path=os.path.join(root, name)
        temp_ticker=temp_path.split('\\')[4]
        temp_text=open(os.path.join(root, name), "r").read(1000000)
        #sec.append(temp_text)
        
        stemp_df= pd.DataFrame(columns=['ticker', 'path', 'string_datetime', 'text'])
        
        try:
            temp_text_obj=re.search(r'(<ACCEPTANCE-DATETIME>)(.*$)', temp_text, re.M|re.I)
        except:
            temp_text=""
            temp_text_obj=re.search(r'(<ACCEPTANCE-DATETIME>)(.*$)', temp_text, re.M|re.I)
       
        try:
            temp_text_dt=temp_text_obj.group(2)
        except:
            temp_text_dt=""
            print("No Datetime Found")
            
        temp_text=REPLACE_NO_SPACE.sub("", temp_text)
        temp_text=REPLACE_WITH_SPACE.sub("", temp_text)

        stemp_df =  stemp_df.append({'ticker': temp_ticker,  'path': temp_path, \
        'string_datetime': temp_text_dt, 'text': temp_text}, ignore_index=True)
            
            
        sentiment_df =  sentiment_df.append(stemp_df, ignore_index=True)

        print("Finished")



sentiment_df.dtypes
sentiment_df['datetime']=0 
sentiment_df['date']=0
for x in range(len(sentiment_df)):
    try:
        year=int(sentiment_df['string_datetime'][x][0:4])
        month=int(sentiment_df['string_datetime'][x][4:6])
        day=int(sentiment_df['string_datetime'][x][6:8])
        hr=int(sentiment_df['string_datetime'][x][8:10])
        minu=int(sentiment_df['string_datetime'][x][10:12])
        sec=int(sentiment_df['string_datetime'][x][12:14])
        sentiment_df.iloc[x, 4]=dt.datetime(year, month, day, hr, minu, sec)
        sentiment_df.iloc[x, 5]=dt.date(year, month, day)
    except:
        sentiment_df.iloc[x, 4]=0
        sentiment_df.iloc[x, 5]=0
        print("No Extractable Date Value") 



sentiment_df=sentiment_df.\
loc[~(sentiment_df['date']==0),:]

sentiment_df=sentiment_df.drop_duplicates(subset=['ticker', 'date'])
sentiment_df.date=pd.to_datetime(sentiment_df.date)

sentiment_df=sentiment_df.sort_values(by=['ticker', 'date'])
sentiment_df=sentiment_df.reset_index(drop=True)
sentiment_df['ticker']=sentiment_df['ticker'].str.strip()

#Bring in And Merge Financial Data
master_finance_df=pd.read_csv("constructed\\capstone\\master_finance_save.csv", sep=',')
master_finance_df= master_finance_df.loc[:, ~master_finance_df.columns.str.contains('^Unnamed')]
master_finance_df=master_finance_df.\
loc[~(master_finance_df['roll_resid'] == 0),:]
master_finance_df.date=pd.to_datetime(master_finance_df.date)
master_finance_df=master_finance_df.reset_index(drop=True)
master_finance_df=master_finance_df.sort_values(by=['ticker', 'date'])
master_finance_df['arith_resid']=master_finance_df['roll_resid'].\
apply(lambda x: math.exp(x)-1)
master_finance_df['ret_ind']=master_finance_df['arith_resid'].\
apply(lambda x: 1 if x >=0  else 0)
master_finance_df['ticker']=master_finance_df['ticker'].str.strip()

master_finance_df.dtypes
sentiment_df.dtypes
analysis_df=pd.merge(master_finance_df, sentiment_df, how='inner', \
on=['ticker', 'date'])
analysis_df=analysis_df.reset_index(drop=True)
mini_sdf=analysis_df[['ticker', 'date', 'path', 'price', 'string_datetime']]


#minidf=sentiment_df[0:3]
#mini_sdf=mini_sdf[['ticker', 'path', 'string_datetime', 'datetime', 'date']]
mini_sdf=sentiment_df[['ticker', 'path', 'string_datetime', 'datetime', 'date']]
minidf=analysis_df[['ticker', 'price', 'arith_resid', 'ret_ind']]
        
from sklearn.feature_extraction.text import CountVectorizer

sec_texts=analysis_df['text']

cv = CountVectorizer(binary=True)
cv.fit(sec_texts)
X = cv.transform(sec_texts)
target=analysis_df['ret_ind']

from sklearn.linear_model import LogisticRegression
#from sklearn.metrics import accuracy_score
#from sklearn.model_selection import train_test_split

lr = LogisticRegression()
results=lr.fit(X, target)
score = lr.score(X, target)
print(score)
        
        
        
