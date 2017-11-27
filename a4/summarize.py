"""
sumarize.py
"""
import json

def main():
    tweets, clusters, positive, neutral, negative = readData()
    users = sum(len(n) for n in clusters)
    with open('summary.txt', 'w',encoding = 'utf-8') as f:
        f.write("Number of users collected: %d\n\n" % users)
        f.write("Number of messages collected: %d\n\n" % len(tweets))
        f.write("Number of communities discovered: %d\n\n" % len(clusters))
        f.write("Average number of users per community: %f\n\n" % (sum(len(n) for n in clusters) / len(clusters)))
        f.write("positive class found %d instiances.\n\n" % len(positive))
        f.write("neutral class found %d instiances.\n\n" % len(neutral))
        f.write("negative class found %d instiances.\n\n" % len(negative))
        f.write("positive class example: \n%s\nscore = %d\n\n" % (positive[0][0],positive[0][1]))
        f.write("neutral class example: \n%s\nscore = %d\n\n" % (neutral[0][0], neutral[0][1]))
        f.write("negative class example: \n%s\nscore = %d\n\n" % (negative[0][0], negative[0][1]))
    print("\nFinished summarize.\n\ndata stored in 'summary.txt'.\n")

def readData():
    tweets = json.loads(open('searchResults.json').read())
    clusters = json.loads(open('clusters.json').read())
    positive = json.loads(open('positive.json').read())
    neutral = json.loads(open('neutral.json').read())
    negative = json.loads(open('negative.json').read())
    return tweets, clusters, positive, neutral, negative

if __name__ == '__main__':
    main()