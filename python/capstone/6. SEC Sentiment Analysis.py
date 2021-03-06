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
import math
import nltk
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix
from sklearn.metrics import classification_report
from sklearn.metrics import f1_score
from sklearn.pipeline import Pipeline
from sklearn.svm import LinearSVC, NuSVC, SVC
from sklearn.neighbors import KNeighborsClassifier
from sklearn.preprocessing import OneHotEncoder, LabelEncoder
from sklearn.linear_model import LogisticRegressionCV,  SGDClassifier
from sklearn.ensemble import BaggingClassifier, ExtraTreesClassifier, RandomForestClassifier
import warnings
warnings.filterwarnings("ignore")

#Create Dataframe of SEC Documents and Extracted Data For Purposes of Sentiment Analysis
words = set(nltk.corpus.words.words())
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
            
        temp_text_c1=temp_text.lower()
        temp_text_c2=re.sub('[^abcdefghijklmnopqrstuvwxyz\s]', '', temp_text_c1)
        temp_text_c3=" ".join(w for w in nltk.wordpunct_tokenize(temp_text_c2) \
                                 if w.lower() in words or not w.isalpha())

        stemp_df =  stemp_df.append({'ticker': temp_ticker,  'path': temp_path, \
        'string_datetime': temp_text_dt, 'text': temp_text_c3}, ignore_index=True)
            
            
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

#sentiment_df.to_csv("constructed\\capstone\\6_code_sentiment_df.csv", sep=',')
sentiment_df=pd.read_csv("constructed\\capstone\\6_code_sentiment_df.csv", sep=',')
sentiment_df=sentiment_df.loc[:, ~sentiment_df.columns.str.contains('^Unnamed')]
sentiment_df=sentiment_df.\
loc[~(sentiment_df['date']<'1999-01-01'),:]
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


#output merged bio stock sample dataframe
bio_merge_sample_df=\
pd.merge(master_finance_df, sentiment_df, how='left', \
on=['ticker', 'date'])
bio_merge_sample_df=\
bio_merge_sample_df[['ticker', 'date', 'sp500', 'price', 'ln_return_index', 'ln_return_price',\
'roll_resid', 'arith_resid', 'path']]
bio_merge_sample_df.to_csv("constructed\\capstone\\bio_merge_sample.csv", sep=',')



analysis_df=pd.merge(master_finance_df, sentiment_df, how='inner', \
on=['ticker', 'date'])
analysis_df=analysis_df.reset_index(drop=True)



sec_texts=analysis_df['text']

#TFID
tf = TfidfVectorizer(binary=True, stop_words='english', max_df=.5, min_df=.01, \
max_features=200)
tf.fit(sec_texts)
X = tf.transform(sec_texts)
y=analysis_df['ret_ind']

X_train, X_test, y_train, y_test = train_test_split(
X, y, train_size = 0.5
)


lr = LogisticRegression()
model = lr.fit(X_train, y_train)
print("Score:")
print(model.score(X_test, y_test))
        
feature_to_coef = {
    word: coef for word, coef in zip(
        tf.get_feature_names(), model.coef_[0]
    )
}
for best_positive in sorted(
    feature_to_coef.items(), 
    key=lambda x: x[1], 
    reverse=True)[:10]:
    print (best_positive)

for best_negative in sorted(
    feature_to_coef.items(), 
    key=lambda x: x[1])[:10]:
    print (best_negative)

y_pred = model.predict(X_test)
print(confusion_matrix(y_test, y_pred))
print(classification_report(y_test, y_pred))


bio_features=sorted(feature_to_coef.items(), key=lambda x: x[1])
bio_features_df=pd.DataFrame(bio_features, columns=['word', 'coef_value'])
bio_features_df.to_csv("constructed\\bio_dataset_features.csv", sep=',')


#TFID, CV
tf = TfidfVectorizer(binary=True, stop_words='english', max_df=.5, min_df=.01, \
max_features=200, ngram_range=(1, 2))
tf.fit(sec_texts)
X = tf.transform(sec_texts)
y=analysis_df['ret_ind']

X_train, X_test, y_train, y_test = train_test_split(
X, y, train_size = 0.5
)


lr = LogisticRegressionCV()
model = lr.fit(X_train, y_train)
print("Score:")
print(model.score(X_test, y_test))
        
feature_to_coef = {
    word: coef for word, coef in zip(
        tf.get_feature_names(), model.coef_[0]
    )
}
for best_positive in sorted(
    feature_to_coef.items(), 
    key=lambda x: x[1], 
    reverse=True)[:10]:
    print (best_positive)

for best_negative in sorted(
    feature_to_coef.items(), 
    key=lambda x: x[1])[:10]:
    print (best_negative)

y_pred = model.predict(X_test)
print(confusion_matrix(y_test, y_pred))
print(classification_report(y_test, y_pred))


#Pipelines:
X=X.toarray()
def score_model(X, y, estimator, **kwargs):
    """
    Test various estimators.
    """ 
    y = LabelEncoder().fit_transform(y)
    model = Pipeline([
         ('one_hot_encoder', OneHotEncoder()), 
         ('estimator', estimator)
    ])

    # Instantiate the classification model and visualizer
    model.fit(X, y, **kwargs)  
    
    expected  = y
    predicted = model.predict(X)
    
    # Compute and return F1 (harmonic mean of precision and recall)
    print("{}: {}".format(estimator.__class__.__name__, f1_score(expected, predicted)))


models = [
    SVC(gamma='auto'), NuSVC(gamma='auto'), LinearSVC(), 
    SGDClassifier(max_iter=100, tol=1e-3), KNeighborsClassifier(), 
    LogisticRegression(solver='lbfgs'), LogisticRegressionCV(cv=3), 
    BaggingClassifier(), ExtraTreesClassifier(n_estimators=100), 
    RandomForestClassifier(n_estimators=100)
]

for model in models:
    score_model(X, y, model)

