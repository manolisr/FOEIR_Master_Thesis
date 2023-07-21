# -*- coding: utf-8 -*-
"""
Created on Thu May 17 17:26:29 2018

@author: Laura
"""
import csv


def createRankingCSV(rankedItems, rankingResultsPath, k, append = False):
    """
    Prints the ranking output to a CSV file.

    @param rankedCandidates: list with ranked candidates
    @param rankingResultsPath: the path for the rankings should look like this
    algorithmName/dataSetName.csv

    no return
    """

    ranking = []#[['userid', 'itemid', 'Original_Score', 'learned_Scores', 'Ranking_Score_from_Postprocessing', 'Sensitive_Attribute']]

    for i in range(k):
        userid = str(int(rankedItems[i].features[0]))
        itemid = str(int(rankedItems[i].features[1]))
        originQ = str(rankedItems[i].originalQualification)
        learned = str(rankedItems[i].learnedScores)
        quali = str(rankedItems[i].qualification)
        proAttr = str(rankedItems[i].isProtected)

        ranking.append([userid, itemid, originQ, learned, quali, proAttr])

    try:
        if not append:
            with open('rankings/' + rankingResultsPath, 'w', newline='') as mf:
                writer = csv.writer(mf)
                writer.writerows(ranking)
        else:
            with open('rankings/' + rankingResultsPath, 'a', newline='') as mf:
                writer = csv.writer(mf)
                writer.writerows(ranking)
    except Exception:
        raise Exception("Some error occured during file creation. Double check specifics.")

def createFinalRankingCSV(rankedItems, rankingResultsPath, k, append = False):
    """
    Prints the ranking output to a CSV file.

    @param rankedCandidates: list with ranked candidates
    @param rankingResultsPath: the path for the rankings should look like this
    algorithmName/dataSetName.csv

    no return
    """

    ranking = []#[['userid', 'itemid', 'score, 'Sensitive_Attribute']]

    for i in range(k):
        userid = str(int(rankedItems[i].features[0]))
        itemid = str(int(rankedItems[i].features[1]))
        # originQ = str(rankedItems[i].originalQualification)
        # learned = str(rankedItems[i].learnedScores)
        # quali = str(rankedItems[i].qualification)
        score = str((k-i)/(k+1))
        proAttr = str(rankedItems[i].isProtected)

        ranking.append([userid, itemid, score, proAttr])

    try:
        if not append:
            with open('rankings/' + rankingResultsPath , 'w', newline='') as mf:
                writer = csv.writer(mf)
                writer.writerows(ranking)
        else:
            with open('rankings/' + rankingResultsPath, 'a', newline='') as mf:
                writer = csv.writer(mf)
                writer.writerows(ranking)
    except Exception:
        raise Exception("Some error occured during file creation. Double check specifics.")

def createPCSV(x, dataSetName, algoName, k=40):
    """
    Prints the values for the doubly stochastic matrix to a csv file 
    rows denote the probability for a document to be ranked at a position from 1 to k
    columns denote the probability for a position to be filled by a document from 1 to k

    @param x: 2D numpy matrix with all entries of the matrix flattened to one entry per row
    @param k: length of the ranking
    @param dataSetName: Name of the data set used for the evaluation
    @param algoName: Name of the algorithm that generated the underlying ranking

    no return
    """

    pResultsPath = algoName + '/' + dataSetName + str(k) + '.csv'

    finalResults = x.tolist()

    try:
        with open('doublyStochasticPropMatrix/' + pResultsPath, 'w', newline='') as mf:
            writer = csv.writer(mf)
            writer.writerows(finalResults)
    except Exception:
        raise Exception("Some error occured during file creation for P. Double check specifics.")