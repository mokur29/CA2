#!/usr/bin/env python

import sys
import datetime
import tweepy
import json
import pandas as pd
# Twitter API credentials
access_token= ''
access_token_secret = ''
consumer_key= ''
consumer_secret = ''

# Authenticate with Twitter API
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth, wait_on_rate_limit=True)

# Calculate the start and end dates for the time range
today = datetime.datetime.today().date()
start_date = today - datetime.timedelta(days=8 * 30)  # 18 months ago
df = pd.DataFrame(columns=['Text', 'Date'],)
# Emit the month and tweet for each retrieved tweet
for topic in ["Dementia", "Mental Health", "Real Health"]:
    for month in [start_date + datetime.timedelta(days=30 * i) for i in range(19)]:
        month_start = month.replace(day=1)
        month_end = month_start + datetime.timedelta(days=30)
        
        # Collect tweets based on the topic and time range
        query = f"{topic} since:{month_start} until:{month_end}"
        tweets = tweepy.Cursor(api.search_tweets, q=query, tweet_mode='extended').items(200)
        
        # Emit the month and tweet as the key-value pair
        j = 0
        for tweet in tweets:
            df = df.append({
            'Date':tweet.created_at,
            'Text':tweet._json
            }, ignore_index=True)
            j = j  + 1
        print(month , j)