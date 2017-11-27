"""
collect.py
"""
from TwitterAPI import TwitterAPI
import sys
import json

consumer_key = '1sRAKQFYCQtLp2kBiVeTiWoHE'
consumer_secret = 'tmE1xkCbePymg8BdcHBLf8inq9vzrQXWXWutkVJHgDlhMpUMLF'
access_token = '711922284642963457-ISXwpbXm7RTi8Rh3EDRIcRhY0ZRatAn'
access_token_secret = 'OLMjfQIFBibMTv8yVhaAmJbf8ifSyccVtIxWqeAvxhUXI'

def main():
    twitter = gettwitter()
    getTweets(twitter, {'q': 'kyrie irving', 'count': 100, 'lang': 'en'})

def gettwitter():
    """ Construct an instance of TwitterAPI using the tokens you entered above.
    Returns:
      An instance of TwitterAPI.
    """
    twitter = TwitterAPI(consumer_key,consumer_secret,access_token,access_token_secret)
    return twitter

def robust_request(twitter, resource, params, max_tries = 5):
    """ If a Twitter request fails, sleep for 15 minutes.
    Do this at most max_tries times before quitting.
    Args:
      twitter .... A TwitterAPI object.
      resource ... A resource string to request; e.g., "friends/ids"
      params ..... A parameter dict for the request, e.g., to specify
                   parameters like screen_name or count.
      max_tries .. The maximum number of tries to attempt.
    Returns:
      A TwitterResponse object, or None if failed.
    """
    for i in range(max_tries):
        request = twitter.request(resource, params)
        if request.status_code == 200:
            return request
        else:
            print('Got error %s \nsleeping for 15 minutes.' % request.text)
            sys.stderr.flush()
            time.sleep(61 * 15)

def getTweets(twitter, searchData):
    """ Search key words and store the result tweets in a file
    Args:
        twitter:
        twitter ...... A TwitterAPI object.
        searchData ... A parameter dict for the request.
    Returns:
        'searchResult.json' ... A json file contain the search result
    """
    tweets = []
    count = 1
    for t in robust_request(twitter, 'search/tweets', searchData):
        tweets.append(t)

    while (count < 10):
        minID = getMinID(tweets)
        searchData['max_id'] = minID - 1
        for t in robust_request(twitter, 'search/tweets', searchData):
            tweets.append(t)
        count += 1

    with open('searchResults.json', 'w', encoding = 'utf-8') as output:
        json.dump(tweets, output)
    print("\nFinished data collection.\n\ndata stored in 'searchResults.json'.\n")

def getMinID(tweets):
    minID = tweets[0]['id']
    for i in range(len(tweets)):
        if minID > tweets[i]['id']:
            minID = tweets[i]['id']
    return minID

if __name__ == '__main__':
    main()