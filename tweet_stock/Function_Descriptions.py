import tweepy
import pprint
import pandas as pd
import numpy as np
import json
import time
from numpy import nan
import re
from datetime import datetime
import pandas_datareader as pdr
%pylab inline


#apply for twitter application codes through this link
consumer_key = 
consumer_secret = 
access_token = 
access_secret = 

#Find tweeterID with this website https://tweeterid.com/
#For this project I chose the biotech company 'Celgene'

celgene_twitter_id = '325497645'
celgene_twitter_name = '@celgene'

####################################
####  Functions ####################
####################################

#Using Tweepy API grab timeline information of the tweet_id, the text, the source of text, and the timestamp of tweet
#Then add it to a list of dictionaries.
def get_user_timeline(consumer_key,consumer_secret,access_token,access_secret,twitter_name,twitter_id):
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_secret)
    api = tweepy.API(auth, wait_on_rate_limit = True,wait_on_rate_limit_notify =True)
    user_timeline = api.user_timeline(celgene_twitter_id)
    tweet_data = []
    for status in tweepy.Cursor(api.user_timeline,id=celgene_twitter_name).items():
        tweet_entry = {'tweet_id': status.id_str,'text':status.text,"source":status.source, "timestamp":status.created_at}
        tweet_data.append(tweet_entry)
    return tweet_data

#Turn list into Pandas dataframe

def pandas_df(data):
    return pd.DataFrame(data)

#Use regular expressions to add all #hashtags, @handels, websites in text
#Make the timestamp into a date object

def grab_hashtags_date_handles(df):
    df['hashtags'] = df.text.str.findall(r'#.*?(?=\.?\s|$)')
    df['handles'] = df.text.str.findall(r'@.*?(?=\.?\s|$)')
    df['websites_in_text'] = df.text.str.findall('http\S+|www.\S+')
    df['date'] = df['timestamp'].dt.date
    df['date'] = pd.to_datetime(df['date'])
    return df

#pip install pandas-datareader
#pct_change documentation = https://stackoverflow.com/questions/20000726/calculate-daily-returns-with-pandas-dataframe
#Use get_yahoo_data to create a pandas dataframe of stock history of selected company through the yahoo finance database
#pct_change to create another series of the percent difference of each close time 
def get_stock_history(symbols,df):
    stock_df = pdr.get_data_yahoo(symbols=symbols, start=df['timestamp'].iloc[-1].date(), end=df['timestamp'].iloc[0].date())
    stock_df.reset_index(inplace = True)
    stock_df['Percent_change'] =  stock_df.Close.pct_change()
    return stock_df


#Count number of tweets per day and perform inner merge on stock history dataframe
#Create a boolean series on whether percent change is positive or negative

def tweet_counts_stock_df(stock_df,df):
    value_counts_by_date = df.date.value_counts()
    value_counts_by_date = value_counts_by_date.to_frame()
    value_counts_by_date.reset_index(inplace=True)
    value_counts_by_date.columns = ['Date','Tweet_counts']
    value_counts_by_date_vol = pd.merge(value_counts_by_date,stock_df,on='Date',how='inner')
    value_counts_by_date_vol = value_counts_by_date_vol.sort_values('Date')
    value_counts_by_date_vol['positive'] = value_counts_by_date_vol.Percent_change > 0
    return value_counts_by_date_vol


#Sort tweet_counts_stock_df dataframe by tweet count
def most_n_tweet_dates(df):
    return df.sort_values('Tweet_counts',ascending = False)


#Customize size of chart data by top n tweet days
def top_n_tweet_days(df,n):
    return df.head(n)



############################################################
###Function Calls###########################################
############################################################

celgene_tweet_data = get_user_timeline(consumer_key,consumer_secret,access_token,access_secret,celgene_twitter_name,celgene_twitter_id)

#Create clean data copy
celgene_df = pandas_df(celgene_tweet_data)
celgene_df_clean = celgene_df.copy()


#celgene_df.info()
#celgene_df.head()

celgene_df = grab_hashtags_date_handles(celgene_df)
#celgene_df.head()

celgene_stock_df = get_stock_history('CELG',celgene_df)
#celgene_stock_df.head()

tweet_counts_stock_df = tweet_counts_stock_df(celgene_stock_df,celgene_df)
#tweet_counts_stock_df.head()

dates_by_tweet_count = most_n_tweet_dates(tweet_counts_stock_df)
#dates_by_tweet_count.head()

top_20_tweet_days = top_n_tweet_days(dates_by_tweet_count,20)
#top_20_tweet_days


##########################################################
###Plots##################################################
##########################################################


#Top 20 Tweet days and how many Tweets each
#Twenty can be changed in the call for the function top_n_tweet_days
def top_n_tweet_day_plot(n,df):
    top_n_tweet_day = top_n_tweet_days(df,n)
    top_n_tweet_day.plot(kind='bar', x=top_n_tweet_day.index,y='Tweet_counts')
    return top_n_tweet_days

#Stock percent change for the top n tweet days colored blue for positive and red for negative
def pos_neg_change_n_most_tweets(df,n):
    top_n_tweet_day = top_n_tweet_days(df,n)
    ax = top_n_tweet_day.plot(kind='bar',color=top_n_tweet_day.positive.map({True:'b',False:'r'}),x=top_n_tweet_day.index,y='Percent_change')
    ax.set_title('Day Percent Change of Dates with most tweets')
    ax.set_xlabel('Date')
    ax.set_ylabel('Percent Change')

 #pos_neg_change_n_most_tweets(dates_by_tweet_count,11)


 ####################################################################
 ######Correlation###################################################
 ####################################################################

 #Simple correlation calculation for#
 #1) Tweet Counts and Percent Change#
 #2) Volume and Percent Change#
 #3) Tweet Counts and Volume#

#value_counts_by_date_vol['Tweet_counts'].corr(value_counts_by_date_vol['Percent_change']) 
#value_counts_by_date_vol['Volume'].corr(value_counts_by_date_vol['Percent_change'])
#value_counts_by_date_vol['Tweet_counts'].corr(value_counts_by_date_vol['Volume'])


#######################################################################
######Write out data as JSON obj#######################################
#######################################################################

# def write_data(tweet_data,file_name):
#     with open(file_name, 'w') as outfile:
#         json.dump(tweet_data,outfile)
# write_data(celgene_tweet_data,'celgene_data.txt')