Capstone: Economic Events
Stephen Sigrist, Jorge de Leon Miranda and Richard Zhai

Abstract: Our project uses data science techniques to build up models for predicting the abnormal returns of publicly traded stocks using financial and economic news. We use Python to collect historical financial data and corresponding news and event data from a variety of sources, including SEC filings, Google Trends, and news articles published online by the Guardian UK, the New York Times, the Wall Street Journal, Blomberg, the Financial Times, and Seeking Alpha. After ingesting, wrangling, and merging the data, we analyze the statistical properties of the estimated abnormal returns themselves and implement a variety of machine learning models to see how well features extracted from the news data can predict directional binary classifications of abnormal returns. We find that the calculated abnormal returns exhibit covariance stationary statistical properties (white noise), as expected. Using TfidfVectorizer and other methods to create features based on n-grams, we find that models predicting binary classifications of abnormal returns top out with accuracy scores below 70% and exhibit F1 scores not much higher than 50%, which is consistent with prior literature. We also use sentiment indicators to predict “large” movements with supervised classification machine learning techniques. Random Forest models perform the best scores and F1 scores are consistent with the main analysis. However, when using per-class model evaluation techniques with Yellowbrick, we find that fitted models are the bestat predicting “small” movements but do a poor job in predicting “large” movements. The results are robust to cross-validation and expanding window cross-validation procedures. An additional finding is that there is little overlap between relevant features extracted with TfidfVectorizer and those predicted by sentiment dictionaries.	

The capstone codes are simply labeled 1 through 8, providing a simple pipeline for replicating the process. Most ingestion is done in the 1 through 3 codes.

https://github.com/georgetown-analytics/Economic-Events/blob/master/python/capstone/1.%20Capstone%20import%20financial.py

https://github.com/georgetown-analytics/Economic-Events/blob/master/python/capstone/2.%20Capstone%20SEC%20Import%20and%20Clean.py

https://github.com/georgetown-analytics/Economic-Events/blob/master/python/capstone/3.%20Capstone%20Scrape%20Google.py

https://github.com/georgetown-analytics/Economic-Events/tree/master/python/Google%20Trends%20API%20Data%20ingestion


This is the code for the Guardian Data Ingestion and Wrangling and Google Trends API. 
https://github.com/georgetown-analytics/Economic-Events/tree/master/python/Google%20Trends%20API%20Data%20ingestion 

https://github.com/georgetown-analytics/Economic-Events/tree/master/python/The%20Guardian%20Data%20ingestion%20and%20wrangling 

The exploratory data analysis can be found here:
https://github.com/georgetown-analytics/Economic-Events/blob/master/python/Exploratory%20Data%20Analysis.ipynb 

The alternative analysis can be found here: 
https://github.com/georgetown-analytics/Economic-Events/blob/master/python/Alternative%20feature%20and%20model%20selectionevaluation.ipynb
