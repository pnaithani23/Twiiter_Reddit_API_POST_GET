#!/usr/bin/env python
import tweepy
import flask
from flask import *
from pydocumentdb import document_client
from azure.cosmos import CosmosClient
import praw
import sys



# Create the application.
APP = flask.Flask(__name__)
APP.secret_key = 'secret key'


#### CosmosDB Creds #####
url = 'Cosmos DB URL'
key = 'Cosmos DB Primary key'



@APP.route('/')
def index():
    """ Displays the index page accessible at '/'
    """
    return flask.render_template('index.html')



##### Reddit Creds #####
reddit = praw.Reddit(client_id='Reddit Access Key',
                     client_secret='Reddit Secret Access Key',
                     user_agent='pnaithani',
                     redirect_uri='http://localhost:8080',
                     refresh_token='Reddit Referesh Token') ### Reddit Referesh Token is generated using token_reddit.py

subr = 'pythonsandlot' # Choose your subreddit
subreddit = reddit.subreddit(subr) # Initialize the subreddit to a variable


@APP.route('/reddit', methods =["GET", "POST"])
def red():
    if request.method == "POST":
       # getting input with name = TWEET_TEXT in HTML form
       TitlE = request.form.get("TITLE_TEXT")
       ContenT = request.form.get("CONTENT_TEXT")
       title_text = 'Thought of the day'
       selftext = ContenT
       subreddit.submit(title_text,selftext=selftext)
    
    client = CosmosClient(url, credential=key)
    database_reddit = 'DMDB'
    database_reddit = client.get_database_client(database_reddit)
    container_reddit = 'reddit'
    container_red = database_reddit.get_container_client(container_reddit)
    
    for submission in reddit.subreddit('Batman').top(limit=11):
        container_red.upsert_item({
            'id': submission.id,
            'text': submission.selftext,
            'url': submission.url,
            'upvotes': submission.score,
            'name': submission.name
            })

    return render_template("Reddit_Post.html")




##### Twitter Creds #####
consumer_key = "Twitter Access Key"
consumer_secret = "Twitter Secret Access Key"
access_token= "Twitter Access Token"
access_token_secret = "Twitter Secret Access Token"

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)

api = tweepy.API(auth)
public_tweets = api.home_timeline()

@APP.route('/twitter', methods =["GET", "POST"])
def twe():
    if request.method == "POST":
       Text_tweet = request.form.get("text") #fetching the data from html form
       api.update_status(Text_tweet)

    ##### Storing Data in CosmosDB #####
    public_tweets = api.home_timeline()
    client = CosmosClient(url, credential=key)
    database_name = 'DMDB'
    database = client.get_database_client(database_name)
    container_name = 'twitter'
    container = database.get_container_client(container_name)

    for tweet in public_tweets:
        tweetsPulled = {}
        tweetsPulled['created_at'] = tweet._json['created_at']
        tweetsPulled['twitter_handler'] = tweet._json['user']['screen_name']
        tweetsPulled['source'] = tweet._json['source']
        tweetsPulled['text'] = tweet._json['text']
        tweety = api.get_status(tweet._json['id'])
        tweetsPulled['likes_count'] = tweet._json['favorite_count']
        container.upsert_item({
            'id': str(tweet._json['id']),
            'source': tweet._json['source'],
            'text': tweet._json['text'],
            'twitter_handler': tweet._json['user']['screen_name'],
            'liked_count': tweet._json['favorite_count'],
            'created_at': tweet._json['created_at']
        })

    return render_template("Twitter_Post.html")


if __name__ == '__main__':
    APP.debug=True
    APP.run()