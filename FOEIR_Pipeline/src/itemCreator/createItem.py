import pandas as pd
import numpy as np
# from src.candidateCreator.candidate import Candidate
from src.itemCreator.item import Item

class createItem():

    def createScoreBased(data):
        """

        @param filename: Path of input file. Assuming CSV with sensitive
        attribute in last column and score second last column. If param features
        is true, we further assume that features are in the remaining first columns

        return    A list with protected candidates, a list with nonProtected candidates
                  and a list with the whole colorblind ranking.
        """

        protected = []
        nonProtected = []
        ranking = []
        i = 0

        for index,row in data.iterrows():
            i += 1
            features = np.asarray(row[:(-2)])
            # access second row of .csv with protected attribute 0 = nonprotected group and 1 = protected group
            if row[-1] == 0:
                nonProtected.append(Item(float(row[-2]), float(row[-2]), [], i, [], features))
            else:
                protected.append(Item(float(row[-2]), float(row[-2]), "protectedGroup", i, [], features))

        ranking = nonProtected + protected

        # sort candidates by credit scores
        protected.sort(key=lambda item: item.qualification, reverse=True)
        nonProtected.sort(key=lambda item: item.qualification, reverse=True)

        # creating a color-blind ranking which is only based on scores
        ranking.sort(key=lambda item: item.qualification, reverse=True)

        for i, candidate in enumerate(ranking):
            candidate.originalIndex = i + 1
            candidate.learnedIndex = i + 1
            candidate.currentIndex = i + 1

        return protected, nonProtected, ranking