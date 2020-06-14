# -*- coding: utf-8 -*-
"""
Created on Sun Mar  1 12:30:27 2020

@author: Stephen Sigrist
"""
import os
os.chdir("..")
import shutil

import pandas as pd
import re
import datetime as dt
import math
import nltk
from sklearn.feature_extraction.text import CountVectorizer
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


        
#make dataframe of tickers to gather data about
tickers_data = pd.read_csv("input files\\capstone\\big ticker list.csv", index_col=False)
#tickers_data=tickers_data[0:3]
tickers_data=tickers_data.reset_index(drop=True)

words = set(nltk.corpus.words.words())

"""
sentiment_df=pd.DataFrame(columns=['ticker', 'path', \
'string_datetime', 'text'])
    

dl = Downloader("downloaded\\big capstone\\SEC")
for i in range(len(tickers_data)):
    print(tickers_data['ticker'][i])
    for filing_type in dl.supported_filings:
        try:
           dl.get(filing_type, tickers_data['ticker'][i], 200)
        except:
            print("An Error Occured While Downloading "+tickers_data['ticker'][i])
   
    for root, dirs, files in os.walk("downloaded\\big capstone\\SEC", topdown=False):
        for name in files:
            #print(name)
            #print(os.path.join(root, name))
        
            temp_path=os.path.join(root, name)
            temp_ticker=temp_path.split('\\')[4]
            #print(temp_ticker)
        
            stemp_df= pd.DataFrame(columns=['ticker', 'path', 'string_datetime', 'text'])
        
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
            
            temp_text_c1=temp_text.lower()
            temp_text_c2=re.sub('[^abcdefghijklmnopqrstuvwxyz\s]', '', temp_text_c1)
            temp_text_c3=" ".join(w for w in nltk.wordpunct_tokenize(temp_text_c2) \
                                 if w.lower() in words or not w.isalpha())

            stemp_df =  stemp_df.append({'ticker': temp_ticker,  'path': temp_path, \
            'string_datetime': temp_text_dt, 'text': temp_text_c3}, ignore_index=True)
            
            temp_text=""
        
            sentiment_df =  sentiment_df.append(stemp_df, ignore_index=True)

    shutil.rmtree("downloaded\\big capstone\\SEC", ignore_errors=True)
    os.mkdir("downloaded\\big capstone\\SEC")
    sentiment_df.to_csv("constructed\\big_runningsave_SEC.csv", sep=',')

sentiment_df.to_csv("constructed\\big_sec_sentiment.csv", sep=',')




sentiment_df=pd.read_csv("constructed\\big_sec_sentiment.csv", \
dtype={'string_datetime': 'object'}, sep=',', nrows=100000)
sentiment_df=sentiment_df.loc[:, ~sentiment_df.columns.str.contains('^Unnamed')]
sentiment_df=sentiment_df.reset_index(drop=True)

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
        
sentiment_df.to_csv("constructed\\big_sec_sentiment.csv", sep=',')
"""
sentiment_df=pd.read_csv("constructed\\big_sec_sentiment.csv", \
dtype={'string_datetime': 'object'}, sep=',', nrows=200000)
sentiment_df=sentiment_df.loc[:, ~sentiment_df.columns.str.contains('^Unnamed')]
sentiment_df=sentiment_df.reset_index(drop=True)



sentiment_df=sentiment_df.\
loc[~(sentiment_df['date']==0),:]

sentiment_df=sentiment_df.drop_duplicates(subset=['ticker', 'date'])
sentiment_df.date=pd.to_datetime(sentiment_df.date)

sentiment_df=sentiment_df.sort_values(by=['ticker', 'date'])
sentiment_df=sentiment_df.reset_index(drop=True)
sentiment_df['ticker']=sentiment_df['ticker'].str.strip()

#Bring in And Merge Financial Data
master_finance_df=pd.read_csv("constructed\\big_stack_backup.csv", sep=',')
master_finance_df= master_finance_df.loc[:, ~master_finance_df.columns.str.contains('^Unnamed')]
master_finance_df=master_finance_df.\
loc[~(master_finance_df['roll_resid'] == 0),:]
master_finance_df=master_finance_df.\
loc[~(master_finance_df['roll_resid'].isnull()),:]
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
analysis_df.dtypes


#subset analysis df by residual size
analysis_df['abs_arith_resid']=abs(analysis_df['arith_resid'])
analysis_df['abs_arith_resid'].describe()
analysis_df['mean_abs_resid']=analysis_df['abs_arith_resid'].mean()
analysis_df['std_abs_resid']=analysis_df['abs_arith_resid'].std()

analysis_df['cutoff_a']=analysis_df['mean_abs_resid']+.5*analysis_df['std_abs_resid']
analysis_df['cutoff_b']=analysis_df['mean_abs_resid']+1*analysis_df['std_abs_resid']

analysis_a_df=analysis_df.\
loc[(analysis_df['abs_arith_resid']>analysis_df['cutoff_a']),:]

analysis_b_df=analysis_df.\
loc[(analysis_df['abs_arith_resid']>analysis_df['cutoff_b']),:]


#model and analyze ALL
sec_texts=analysis_b_df['text']

#TFID
tf = TfidfVectorizer(binary=True, stop_words='english', max_df=.5, min_df=.01, \
max_features=2000)
tf.fit(sec_texts)
X = tf.transform(sec_texts)
y=analysis_b_df['ret_ind']

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


all_features=sorted(feature_to_coef.items(), key=lambda x: x[1])
all_features_df=pd.DataFrame(all_features, columns=['word', 'coef_value'])
all_features_df.to_csv("constructed\\large_dataset_features.csv", sep=',')


#TFID, CV
tf = TfidfVectorizer(binary=True, stop_words='english', max_df=.5, min_df=.01, \
max_features=200, ngram_range=(1, 2))
tf.fit(sec_texts)
X = tf.transform(sec_texts)
y=analysis_b_df['ret_ind']

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
