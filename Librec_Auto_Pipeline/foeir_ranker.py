# from src.candidateCreator.createCandidate import createCandidate as cC
from src.itemCreator.createItem import createItem as cI
# from src.csvProcessing.csvPrinting import createRankingCSV
from printing import createRankingCSV, createFinalRankingCSV
from src.algorithms.fair_ranker.runRankFAIR import runFAIR
from src.algorithms.LFRanking.runLFRanking import runLFRanking
from src.algorithms.FeldmanEtAl.runFeldmanEtAl import feldmanRanking
from src.algorithms.FOEIR.runFOEIR import runFOEIR
from src.algorithms.ListNet.runListNet import runListNet
from src.measures.runMetrics import runMetrics
from src.visualizer.visualizeData import plotData
import src.measures.finalEvaluation as finalEval
import os
import pandas as pd
import numpy as np
import csv
import datetime

def scoreBasedEval(user_recs, dataSetName, dataSetPath, n = 40, k = 10, features = True, protected = [], nonProtected = [], originalRanking = [], listNet = False):

    """
    Evaluates the learning to rank algorithms and runs
    the optimization and evaluation of the post-processing methods

    @param dataSetName: Name of the data set
    @param dataSetPath: Path of the data sets for score based evaluation.
    @param k: Provides the length of the ranking
    @param features: True if the provided data set has features for LFRanking, otherwise
    false
    @param protected: If data comes from a learning to rank algorithm this param holds a
    list of candidates with protected group membership
    @param protected: If data comes from a learning to rank algorithm this param holds a
    list of candidates with non-protected group membership
    @param protected: If data comes from a learning to rank algorithm this param holds a
    list of candidates from the new ranking
    @param scoreData: Is set false if the data does not come from an already scored data
    set but from a learning to rank algorithm

    returns a list of evaluation results of the form:
        [dataSetName, Optimization Algorithm, Measure, Value of Measure]
    """

    evalResults = []

    # initialize k for evaluation purposes. This k is also used for calculation of FOIER algorithms
    evalK = n

    # check if evalK is not larger than 40
    if evalK > 40:
        print('Evaluations only done for k = 40 due to comparability reasons. Rankings are still created for  ' +str
            (n ) +'. If changes to this are wished, please open runBenchmarking and change line 226 accordingly.')
        evalK = 40

    # check if the given data comes from the base line algorithm ListNet
    # if it does not, construct candidates from the data
    # if listNet == False:
        # creates Candidates from the preprocessed CSV files in folder preprocessedDataSets
    protected, nonProtected, originalRanking = cI.createScoreBased(user_recs)

    # creates a csv with candidates ranked with color-blind ranking
    #createRankingCSV(originalRanking, 'Color-Blind/' + dataSetName + 'ranking.csv', n)
    # run the metrics ones for the color-blind ranking
    #evalResults += (runMetrics(evalK, protected, nonProtected, originalRanking, originalRanking, dataSetName, 'Color-Blind'))

    # # create ranking like Feldman et al.
    # feldRanking, pathFeldman = feldmanRanking(protected, nonProtected, k, dataSetName)
    # # Update the currentIndex of a candidate according to feldmanRanking
    # feldRanking = updateCurrentIndex(feldRanking)
    # # create CSV with rankings from FAIR
    # createRankingCSV(feldRanking, pathFeldman, k)
    # # evaluate FAIR with all available measures
    # evalResults += (
    #     runMetrics(evalK, protected, nonProtected, feldRanking, originalRanking, dataSetName, 'FeldmanEtAl'))

    # run evaluations for FOEIR with different Fairness Constraints
    # we only produce rankings of k = 50 since construction of P as well as dicomposition of Birkhoff take a very long time
    # and consume a lot of memory.
    # run for FOEIR-DPC
    dpcRanking, dpcPath, isDPC = runFOEIR(originalRanking, dataSetName, 'FOEIR-DPC', evalK)
    if isDPC == True:
        dpcRanking = updateCurrentIndex(dpcRanking)
        createFinalRankingCSV(dpcRanking, dpcPath, k, True)
        #evalResults += (runMetrics(evalK, protected, nonProtected, dpcRanking, originalRanking, dataSetName, 'FOEIR-DPC'))

    dtcRanking, dtcPath, isDTC = runFOEIR(originalRanking, dataSetName, 'FOEIR-DTC', evalK)
    if isDTC == True:
        dtcRanking = updateCurrentIndex(dtcRanking)
        createFinalRankingCSV(dtcRanking, dtcPath, k, True)
        #evalResults += (runMetrics(evalK, protected, nonProtected, dtcRanking, originalRanking, dataSetName, 'FOEIR-DTC'))

    dicRanking, dicPath, isDIC = runFOEIR(originalRanking, dataSetName, 'FOEIR-DIC', evalK)
    if isDIC == True:
        dicRanking = updateCurrentIndex(dicRanking)
        createFinalRankingCSV(dicRanking, dicPath, k, True)
        #evalResults += (runMetrics(evalK, protected, nonProtected, dicRanking, originalRanking, dataSetName, 'FOEIR-DIC'))

    # # run evaluations for FAIR
    # # run FAIR algorithm
    # FAIRRanking, notSelected, pathFAIR = runFAIR(dataSetName, protected, nonProtected, k)
    # # Update the currentIndex of a candidate according to FAIR
    # FAIRRanking = updateCurrentIndex(FAIRRanking)
    # # create CSV with rankings from FAIR
    # createRankingCSV(FAIRRanking, pathFAIR, k)
    # # evaluate FAIR with all available measures
    # evalResults += (runMetrics(evalK, protected, nonProtected, FAIRRanking, originalRanking, dataSetName, 'FAIR'))

    # if features:
    #     try:
    #         # run evaluations for LFRanking
    #         # run LFRanking algorithm
    #         LFRanking, pathLFRanking = runLFRanking(originalRanking, protected, nonProtected, 4, dataSetName)
    #         # create CSV file with ranking outputs
    #         createRankingCSV(LFRanking, pathLFRanking, k)
    #         # Update the currentIndex of a candidate according to LFRanking
    #         LFRanking = updateCurrentIndex(LFRanking)
    #         # evaluate LFRanking with all available measures
    #         evalResults += (
    #             runMetrics(evalK, protected, nonProtected, LFRanking, originalRanking, dataSetName, 'LFRanking'))
    #     except Exception:
    #         print('Could not create LFRanking for ' + dataSetName)
    #         pass

    return evalResults


def updateCurrentIndex(ranking):
    """
    Updates the currentIndex of a ranking according to the current order in the
    list
    @param ranking: list with candidates of a ranking

    return list of candidates with updated currentIndex according to their
    position in the current ranking

    """

    index = 0

    for i in range(len(ranking)):
        index += 1

        ranking[i].currentIndex = index

    return ranking