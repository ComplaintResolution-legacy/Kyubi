from slistener import SListener
import tweepy
import traceback
import os
import json

twitter_cred = json.loads(os.environ['TWITTER_CRED'])


consumer_key = twitter_cred['consumer_key']
consumer_secret = twitter_cred['consumer_secret']
access_token = twitter_cred['access_token']
access_token_secret = twitter_cred['access_token_secret']

# OAuth process, using the keys and tokens
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)

# Creation of the actual interface, using authentication
api = tweepy.API(auth)

def main():
    track = ['#LNMComplaint']
 
    listen = SListener(api)
    stream = tweepy.Stream(auth, listen)

    print("Streaming started...")

    try: 
        stream.filter(track = track)
    except Exception as e:
        print(traceback.print_exc())
        stream.disconnect()

if __name__ == '__main__':
    main()