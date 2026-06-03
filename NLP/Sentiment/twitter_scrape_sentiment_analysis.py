#pip install textblob  #processing library for textual data
#pip install tweepy #twitter open source api
from textblob import TextBlob 
import tweepy
import sys 

not_telling_you = open('/Users/clairekraft/Desktop/Python/AI/T_API.txt','r').read().splitlines()
key = not_telling_you[0]
key_secret = not_telling_you[1]
access_token = not_telling_you[2]
access_secret = not_telling_you[3]

# authentication
auth_handler = tweepy.OAuthHandler(consumer_key = key, consumer_secret = key_secret)
auth_handler.set_access_token(access_token, access_secret)

# connect to API
api = tweepy.API(auth_handler)

# choose your interest
search_term = 'stocks'
tweet_amount = 200 

# using the cursor object (method, argument for method, language for method )
tweets = tweepy.Cursor(api.search_tweets, q=search_term, lang = 'en').items(tweet_amount)

#setting up pplarity for sentiment analysis
polarity = 0
positive = 0
negative = 0
neutral = 0 

for tweet in tweets:
    #print(tweet.text) # uncleaned up text output

    #let's do some text cleaning
    final_text = tweet.text.replace('RT', '') #taking out RT
    if final_text.startswih(' @'):
        position = final_text.index(' : ')
        final_text = final_text[position+2:] #taking out @username handle
    if final_text.startswih('@'):
        position = final_text.index(' ')
        final_text = final_text[position+2:]
    analysis = TextBlob(final_text)
    tweet_polarity = analysis.polarity
    if tweet_polarity > 0.00:
        positive +=1
    elif tweet_polarity < 0.00:
        negative += 1
    elif tweet_polarity: #only if is exactly 0.00
        neutral += 1
    polarity += tweet_polarity
    #print(final_text)


print(polarity)
print(f'Amount of positive tweets:{positive}')
print(f'Amount of positive tweets:{negative}')
print(f'Amount of positive tweets:{neutral}')
