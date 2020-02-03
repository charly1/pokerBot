# -*- coding: utf-8 -*-
"""
Created on Wed Jan 15 16:14:32 2020

@author: Charly
"""

import operator as op
from functools import reduce
import math
import numpy as np


def ncr(n, r):
    r = min(r, n-r)
    numer = reduce(op.mul, range(n, n-r, -1), 1)
    denom = reduce(op.mul, range(1, r+1), 1)
    return int(numer / denom)

def cardFamilyToId(card):
    strCmp = "23456789"
    strCmpH = "JQKA"
    if "10" in card:
        idTmp = 8
    elif card[0] in strCmp:
        idTmp = int(card[0])-2
    elif card[0] in strCmpH:
        idTmp = strCmpH.find(card[0])+9
    else:
        idTmp = -1
    return idTmp
    

def probPair(N,cards):
    nbCards = len(cards)
    tmpVect = np.zeros((13))
    flagIsApair = False
    for i in range(nbCards):
        idTmp = cardFamilyToId(cards[i])
        if tmpVect[idTmp] == 0:
            tmpVect[idTmp] = 1
        else:
            flagIsApair = True
            break
        
    if flagIsApair == True:
        Ptot = 100
    elif nbCards == 2:
        P1 = (4*N-8)/(4*N-2)
        P2 = (4*N-12)/(4*N-3)
        P3 = (4*N-16)/(4*N-4)
        P4 = (4*N-20)/(4*N-5)
        P5 = (4*N-3*6)/(4*N-6)
        Ptot = P1*P2*P3*P4*P5
    return Ptot

N = 13; #nb of type of cards
C = 7;  #nb cards to cumulate 

# spade, club, heart or diamond. 
cards = ["As","4h"]

nbCombTot=ncr(4*N,C)

print(nbCombTot)
# # nbPair = ncr(N,1)*ncr(4,2)*ncr(N-1,3)*math.pow(ncr(4,1),3)
# nbPair = 64
# for i in range(C-1):
#     nbPair=nbPair*(N-i)
# print(nbPair)
print(probPair(N,cards))
# print(cardFamilyToId("As"))





