#coding = utf8

import csv
import numpy as np

# DATASET = 'data/EmotionSongs/Dataset'
DATASET = 'data/GTZAN/Dataset'
# CLASS = 4
CLASS = 10
feature_types = ['mvd', 'rh', 'rp', 'ssd', 'trh', 'tssd']


name2label = {}
categories = {}
def loadLabel():
    label_file = open(DATASET + '/labels.csv', 'r')
    for line in label_file:
        line = line.split('####')
        line  = [item.strip() for item in line]

        name = line[0]
        label = int(line[1])
        category = int(line[2])

        name2label[name] = label
        categories[label] = category
    label_file.close()

def calculateDist(va, vb):
    va = np.array(va)
    vb = np.array(vb)
    return np.sqrt(sum((va - vb) ** 2))

def rank(feature):
    data_file = open(DATASET + '/%s.csv' % feature, 'r')
    reader = csv.reader(data_file)
    songs = {}
    for line in reader:
        songs[int(name2label[line[0]])] = map(float, line[1 : -1])
    rank_file = open(DATASET + '/%s_rank.csv' % feature, 'w')
    writer = csv.writer(rank_file)
    count = 0
    for s in songs:
        count += 1
        print "%s\t%d" % (feature, count)
        dist = {}
        for t in songs:
            if s == t: continue
            dist[t] = calculateDist(songs[s], songs[t])
        dist = sorted(dist.iteritems(), key = lambda item: item[1])
        dist = [item[0] for item in dist]
        dist = [s] + dist
        writer.writerow(dist)
    rank_file.close()
    data_file.close()

K = 20

def calculateJaccard(va, vb):
    va = set(va); vb = set(vb)
    return float(len(va & vb)) / len(va | vb)

def rerank(feature):
    data_file = open(DATASET + '/%s_rank.csv' % feature, 'r')
    reader = csv.reader(data_file)
    rank = {}
    for line in reader:
        line = map(int, line)
        rank[line[0]] = line[1 : -1]
    data_file.close()

    rerank_file = open(DATASET + '/%s_rerank.csv' % feature, 'w')
    writer = csv.writer(rerank_file)
    count = 0
    for s in rank:
        count += 1
        print '%s\t%d' % (feature, count)
        jaccard = {}
        for t in rank[s][0 : 2 * K]:
            jaccard[t] = calculateJaccard(rank[s][0 : 2 * K], rank[t][0 : 2 * K])
        jaccard = sorted(jaccard.iteritems(), key = lambda item: item[1], reverse = True)
        jaccard = [item[0] for item in jaccard]
        jaccard = [s] + jaccard[0 : K]
        writer.writerow(jaccard)  
    rerank_file.close()


def knnAfterRerank(feature, K = K):
    rerank_file = open(DATASET + '/%s_rerank.csv' % feature, 'r')
    reader = csv.reader(rerank_file)
    vote = {}
    predict = {}
    for line in reader:
        line = map(int, line)
        vote[line[0]] = [0] * CLASS
        for i in range(1, K + 1):
            vote[line[0]][categories[line[i]]] += 1
        predict[line[0]] = vote[line[0]].index(max(vote[line[0]]))
    rerank_file.close()
    return predict

def evaluate(predict):
    count = 0
    for song in predict:
        if predict[song] == categories[song]: count += 1
    return float(count) / len(predict)

def knnBeforeRerank(feature, K = K):
    rank_file = open(DATASET + '/%s_rank.csv' % feature, 'r')
    reader = csv.reader(rank_file)
    vote = {}
    predict = {}
    for line in reader:
        line = map(int, line)
        vote[line[0]] = [0] * CLASS
        for i in range(1, K + 1):
            vote[line[0]][categories[line[i]]] += 1
        predict[line[0]] = vote[line[0]].index(max(vote[line[0]]))
    rank_file.close()
    return predict

if __name__ == '__main__':
    loadLabel()
    # for f in feature_types: rank(f)
    # for f in feature_types: rerank(f)
    for f in feature_types:
        print f
        predict_knn = knnBeforeRerank(f)
        accuray_knn = evaluate(predict_knn)
        predict_rerank_knn = knnAfterRerank(f)
        accuray_rerank_knn = evaluate(predict_rerank_knn)
        print "%10.6f\t%10.6f" % (accuray_knn, accuray_rerank_knn)
    