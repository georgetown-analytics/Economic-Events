# -*- coding: utf-8 -*-
"""
Created on Fri May 29 20:18:16 2020

@author: Stephen Sigrist
"""
import os
os.chdir("..")



import pandas as pd
import statsmodels.api as sm
import math


master_finance_df=pd.read_csv("constructed\\capstone\\master_finance_save.csv", sep=',')
master_finance_df= master_finance_df.loc[:, ~master_finance_df.columns.str.contains('^Unnamed')]
master_finance_df=master_finance_df.\
loc[~(master_finance_df['roll_resid'] == 0),:]
master_finance_df=master_finance_df.reset_index(drop=True)
master_finance_df=master_finance_df.sort_values(by=['ticker', 'date'])
master_finance_df['arith_resid']=master_finance_df['roll_resid'].\
apply(lambda x: math.exp(x)-1)
master_finance_df['ret_ind']=master_finance_df['arith_resid'].\
apply(lambda x: 1 if x >=0  else 0)

sec_df=pd.read_csv("constructed\\capstone\\capstone_tabulated_sec.csv", sep=',')
sec_df= sec_df.loc[:, ~sec_df.columns.str.contains('^Unnamed')]
sec_df=sec_df.\
loc[~(sec_df['date'] <'2000-01-01'),:]
sec_df['total_sec_words']=sec_df['poswords']+sec_df['negwords']
sec_df['pos_sec_portion']=sec_df['poswords']/sec_df['total_sec_words']
sec_df=sec_df.reset_index(drop=True)
sec_df=sec_df.sort_values(by=['ticker', 'date'])

sec_df=sec_df[['ticker', 'date', 'poswords', 'negwords', 'pos_sec_portion']]

analysis_df=pd.merge(master_finance_df, sec_df, how='inner', \
on=['ticker', 'date'], validate='one_to_one')
analysis_df=analysis_df.reset_index(drop=True)
analysis_df=analysis_df.sort_values(['ticker', 'date'])

X_port=analysis_df['pos_sec_portion']
X_counts=analysis_df[['poswords','negwords']]
y_cont=analysis_df['arith_resid']
y_disc=analysis_df['ret_ind']

model_cont_port = sm.OLS(y_cont, sm.add_constant(X_port), missing='drop').fit()
model_cont_counts = sm.OLS(y_cont, sm.add_constant(X_counts), missing='drop').fit()
model_disc_port = sm.Probit(y_disc, sm.add_constant(X_port), missing='drop').fit()
model_disc_counts = sm.Probit(y_disc, sm.add_constant(X_counts), missing='drop').fit()


toprint_cont_port = model_cont_port.summary()
toprint_cont_counts = model_cont_counts.summary()
toprint_disc_port  = model_disc_port.summary()
toprint_disc_counts = model_disc_counts.summary()

print("cont_port")
print(toprint_cont_port)
print("cont_counts")
print(toprint_cont_counts)
print("disc_port")
print(toprint_disc_port)
print("disc_counts")
print(toprint_disc_counts)


ypred_disc_port=model_disc_port.predict(sm.add_constant(X_port))
ypred_disc_port=ypred_disc_port.rename("pred_value")
pred_df=y_disc.to_frame().join(ypred_disc_port.to_frame())
pred_df['prediction']=pred_df['pred_value'].\
apply(lambda x: 1 if x >=.5  else 0)

def succ(x):
  if x['prediction'] == x['ret_ind']:
    return 1
  else:
    return 0

pred_df['succes'] = pred_df.apply(succ, axis=1)
pred_df.describe()
