"""
classify.py
"""
import json
from zipfile import ZipFile
from io import BytesIO
from urllib.request import urlopen
import re

def main():
    tweets = readData()
    tokens = tokenize(tweets)
    afinn = getAFINN()
    positive, neutral, negative = rateTweet(tokens, tweets, afinn)
    output('positive.json', positive)
    output('neutral.json', neutral)
    output('negative.json', negative)
    print("\nFinished data classify.\n\ndata stored in 'positive.json', 'neutral.json' and 'negative.json'.\n")

def readData():
    """ read the data collected in the 'collect.py'
    Return:
        tweets ... a json object with tweets.
    """
    tweets = json.loads(open('searchResults.json').read())
    return tweets

def tokenize(tweets):
    '''Utility function to clean tweet text by removing links, special characters
    using simple regex statements.
    '''
    tokens = []
    for tweet in tweets:
        tweet = ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)", " ", tweet['text']).lower().split())
        tweet = re.sub('((www\.[^\s]+)|(https?://[^\s]+))', ' ', tweet).split()
        tokens.append(tweet)
    return tokens

def getAFINN():
    """Download latest AFINN data
    Returns:
        Dictionary of sentimentally rated words
    """

    url = urlopen('http://www2.compute.dtu.dk/~faan/data/AFINN.zip')
    zipfile = ZipFile(BytesIO(url.read()))
    afinn_file = zipfile.open('AFINN/AFINN-111.txt')
    afinn = dict()
    for line in afinn_file:
        parts = line.strip().split()
        if len(parts) == 2:
            afinn[parts[0].decode("utf-8")] = int(parts[1])

    return afinn

def afinnSentiment(afinn, feats):
    '''compute afinn score for each tokens
    return:
        score ... afinn sentiment score of token
    '''
    score = 0
    for f in feats:
        if f in afinn:
            score += afinn[f]
    return score

def rateTweet(tokens, tweets,afinn):
    '''rate tweets sentiment use afinn sentiment analyze
    return:
        positive ... a list with positive score (tweet, score) tuple
        neutral .... a list with neutral score (tweet, score) tuple
        negative ... a list with negative score (tweet, score) tuple
    '''
    positive = []
    neutral = []
    negative = []
    for token, tweet in zip(tokens,tweets):
        score = afinnSentiment(afinn, token)
        if score > 0:
            positive.append((tweet['text'], score))
        elif score == 0 :
            neutral.append((tweet['text'], score))
        else:
            negative.append((tweet['text'], score))
    return positive, neutral, negative

def output(filename, data):
    with open(filename, 'w', encoding = 'utf-8') as f:
        json.dump(data, f)

if __name__ == '__main__':
    main()