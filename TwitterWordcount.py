# Coding question for Square
__author__ = 'Zach Dexter'

import urllib
import urllib2
import json
import re
import sys

class WordCounter:
    def __init__(self,words):
        self._words = words
    def _addToDict(self, item, myDict):
        """
        Append a word to the dictionary passed in (if seen for the firs time)
            or increases the counter for that word (if already seen).
        """
        if item in myDict:
            myDict[item] = myDict[item] + 1
        else:
            myDict[item] = 1
    def add_words(self, data):
        """
        Get a list of all 'words,' defined for our purposes to be any strings
            of alphanumeric characters.
        """
        for s in re.findall(r'\w+', data):
            self._addToDict(s, self._words)
        return self._words
            
class TweetGetter:
    """
    Class for printing a list of the most frequently-used words in someone's tweets.
    
    Usage:
    
    t = TweetGetter('MyTwitterUsername')
    t.wordsByFrequency()
    """
    _resourceURL = "http://api.twitter.com/1/statuses/user_timeline.format"
    def __init__(self, username, limit=1000):
        self._username = username
        self._limit = 1000
        self._tweets = []
        
        # See how many tweets the user has, so we don't try to retrieve more than that later on.
        values = {
            'screen_name': self._username,
        }
        data = urllib.urlencode(values)
        try:
            response = urllib2.urlopen("http://api.twitter.com/1/users/show.json?"+data)
        except urllib2.HTTPError as e:
            sys.stderr.write('Invalid API request.  The screen name you entered may not exist.\n')
            sys.exit()
        
        json_response = json.loads(response.read())
        self._num_tweets = json_response['statuses_count']
    
    def _getTweets(self,last_tweet_id):
        """
        Append the user's last tweets to our internal list of tweets, up to the maximum number allowed by twitter,
            descending, starting at tweet with id /last_tweet_id/.
        Returns the ID of the last tweet grabbed, so that callers know where to start at next time.
        """
        values = {
            'screen_name': self._username,
            'count': 200,
            'include_rts': 1,
        }
        if last_tweet_id > 0:
            values['max_id'] = last_tweet_id
        
        data = urllib.urlencode(values)
        response = urllib2.urlopen("http://api.twitter.com/1/statuses/user_timeline.json?"+data)
        json_response = json.loads(response.read())
        
        for tweet in json_response:
            self._tweets.append(tweet['text'])
        last_tweet_id = json_response[-1]['id_str']

        return len(json_response), last_tweet_id
    def _getTweetsToLimit(self):
        """
        Call _getTweets to fetch the user's last /_limit/ tweets, account for Twitter's per-request limit with a loop.
        Returns our internal list of tweets.
        """
        currentCount = len(self._tweets)
        num_tweets_added = 0
        last_tweet_id = 0
        while (currentCount < self._num_tweets) and (currentCount < self._limit):
            num_tweets_added, last_tweet_id = self._getTweets(last_tweet_id)
            currentCount += num_tweets_added
        return self._tweets
    
    def _uniqueWordsInStatuses(self):
        """ Returns a dictionary of every: {unique word in the user's last /_limit/ statuses, # of occurences of that word}. """
        data = self._getTweetsToLimit()
        data = ' '.join(data) # Make list of tweets into a string
        words = {}
        word_counter = WordCounter(words)
        word_counter.add_words(data)
        return words
    
    def wordsByFrequency(self):
        """ Print a list of words used in the user's last /limit/ statuses,
            sorted by frequency descending.
        """
        unsorted_word_dict = self._uniqueWordsInStatuses()
        for k, v in sorted(unsorted_word_dict.iteritems(), key=lambda (k,v): (v,k),reverse=True):
            print v