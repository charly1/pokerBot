# -*- coding: utf-8 -*-
"""
Created on Wed Jan 15 16:14:32 2020

@author: Charly
"""

# import operator as op
# from functools import reduce
# import math
import numpy as np
from random import randrange
import copy

class Card():
    def __init__(self,strCard):
        self.v = self.extractValue(strCard)
        self.f = self.extractFamily(strCard)
        
    def extractValue(self,strCard):
        strCmp = "23456789"
        strCmpH = "JQKA"
        if "10" in strCard:
            value = "10"
        elif strCard[0] in strCmp:
            value = strCard[0]
        elif strCard[0] in strCmpH:
            value = strCard[0]
        else:
            value = -1
        return value
    
    def extractFamily(self,strCard):
        strCmp = "shdc"
        if strCard[-1] in strCmp:
            value = strCard[-1]
        else:
            value = -1
        return value
    
def genrateHandFromStrList(listStrCards):
    for i in range(len(listStrCards)):
        listStrCards[i] = Card(listStrCards[i])
    return listStrCards
    
def printDeck(deck):
    for i in range(len(deck)):
        print(deck[i].v,deck[i].f)
    print("")
    
def generateDeck():
    strValue = ["2","3","4","5","6","7","8","9","10","J","Q","K","A"]
    strFamily = ["h","s","c","d"]
    
    deck = []
    for i in range(len(strValue)):
        for j in range(len(strFamily)):
            deck.append(Card(strValue[i]+strFamily[j]))
    return deck

def sortDeckHighCard(deck):
    vectTmp = []
    strValue = ["2","3","4","5","6","7","8","9","10","J","Q","K","A"]
    for i in range(len(deck)):
        vectTmp.append(strValue.index(deck[i].v))
    deck = [deck[i] for i in np.argsort(vectTmp)[::-1]]
    return deck
        
    
def generateRandomCard(deck):
    card = deck[randrange(len(deck))]
    deck = removeCardFromDeck(deck,card)
    return card,deck

def completeHandWithRandomcards(nbCardTotal,cardsTmp,deck):
    cards = copy.copy(cardsTmp)
    for i in range(nbCardTotal-len(cards)):
        randCard,deck = generateRandomCard(deck)
        cards.append(randCard)
    return cards,deck

def removeCardFromDeck(deckTmp,card):
    deck = copy.copy(deckTmp)
    if type(card).__name__ != "list":
        card = [card]
    for j in range(len(card)):
        for i in range(len(deck)):
            if deck[i].v == card[j].v and deck[i].f == card[j].f:
                deck.remove(deck[i])
                break
    return deck

def getBestHand(hand):
    flagColor,highCardColor,vectColor = testColor(hand)
    flagSuite,highCardSuite,vectSuite = testSuite(hand)
    flagQuinteFlush = False
    if flagColor == True:
        flagColorQuinte,highCardColorQuinte,vectColorQuinte = testColor(hand,quinteFlushTest=True)
        flagQuinteFlush,highCardQuinteFlush,vectQuinteFlush = testSuite(vectColorQuinte)
    combo,highCardCombo,vectCombo = testNbCardSameValue(hand)
    if flagQuinteFlush == True:
        comboFinal = "quinte flush"
        highCard = highCardQuinteFlush
        handSelected = vectQuinteFlush
    elif combo == "carre":
        comboFinal = "carre"
        highCard = highCardCombo
        handSelected = vectCombo
    elif combo == "full":
        comboFinal = "full"
        highCard = highCardCombo
        handSelected = vectCombo
    elif flagColor == True:
        comboFinal = "color"
        highCard = highCardColor
        handSelected = vectColor
    elif flagSuite == True:
        comboFinal = "suite"
        highCard = highCardSuite
        handSelected = vectSuite
    elif combo == "brelan":
        comboFinal = "brelan"
        highCard = highCardCombo
        handSelected = vectCombo
    elif combo == "double pair":
        comboFinal = "double pair"
        highCard = highCardCombo
        handSelected = vectCombo
    elif combo == "pair":
        comboFinal = "pair"
        highCard = highCardCombo
        handSelected = vectCombo
    else:
        comboFinal = "none"
        hand = sortDeckHighCard(hand)
        highCard = hand[0].v
        handSelected = hand[0:5]

    return comboFinal,highCard,handSelected


        
    
def testNbCardSameValue(hand):
    vect = np.zeros(13)
    strValue = ["2","3","4","5","6","7","8","9","10","J","Q","K","A"]
    for i in range(len(hand)):
        vect[strValue.index(hand[i].v)] += 1
    maxSameValue = int(np.max(vect))
    argmaxSameValue = np.argmax(vect)
    highCard = strValue[argmaxSameValue]
    vect[argmaxSameValue] = 0
    secMaxSameValue = np.max(vect)
    lowCard = strValue[np.argmax(vect)]

    
    if maxSameValue == 4:
        combo = "carre"
    elif maxSameValue == 3 and secMaxSameValue == 2:
        combo = "full"
    elif maxSameValue == 3:
        combo = "brelan"
    elif maxSameValue == 2 and secMaxSameValue == 2:
        combo = "double pair"
        if strValue.index(highCard) < strValue.index(lowCard):
            tmp = highCard
            highCard = lowCard
            lowCard = tmp
    elif maxSameValue == 2:
        combo = "pair"
    else:
        combo = "none"
    
    vectTmp = []
    if combo != "none":
        for i in range(len(hand)):
            if hand[i].v == highCard:
                vectTmp.append(hand[i])
        handLeft = removeCardFromDeck(hand,vectTmp)
        if combo in ["full","double pair"]:
            highCard = [highCard,lowCard]
            for i in range(len(handLeft)):
                if handLeft[i].v == lowCard:
                    vectTmp.append(handLeft[i])
            handLeft = removeCardFromDeck(hand,vectTmp)
    else:
        handLeft = hand
        
    handLeft = sortDeckHighCard(handLeft)
    for i in range(5-len(vectTmp)):
        vectTmp.append(handLeft[i])

    return combo,highCard,vectTmp

    
def testColor(hand,quinteFlushTest=False):
    flagColor = False
    nbH = 0
    nbS = 0
    nbC = 0
    nbD = 0
    vectHeart = []
    vectSpade = []
    vectClub = []
    vectDiamond = []
    vect = []
    for i in range(len(hand)):
        if hand[i].f == "h":
            nbH += 1
            vectHeart.append(hand[i])
        elif hand[i].f == "s":
            nbS += 1
            vectSpade.append(hand[i])
        elif hand[i].f == "c":
            nbC += 1
            vectClub.append(hand[i])
        elif hand[i].f == "d":
            nbD += 1
            vectDiamond.append(hand[i])
    if nbH >= 5:
        flagColor = True
        vect = vectHeart
    elif nbS >= 5:
        flagColor = True
        vect = vectSpade
    elif nbC >= 5:
        flagColor = True
        vect = vectClub
    elif nbD >= 5:
        flagColor = True
        vect = vectDiamond
        
    if flagColor == True:
        vectTmp = []
        strValue = ["2","3","4","5","6","7","8","9","10","J","Q","K","A"]
        for i in range(len(vect)):
            vectTmp.append(strValue.index(vect[i].v))
        maxVal = np.max(vectTmp)
        highCard = strValue[maxVal]
        vectSort = np.sort(vectTmp)[::-1]
        order = np.argsort(vectTmp)[::-1]
        if quinteFlushTest == False:
            vectSort = vectSort[0:5]
            order = order[0:5]

        vect = [vect[i] for i in order]
    else:
        highCard = "none"
    return flagColor,highCard,vect

def testSuite(hand):
    flagSuite = False
    vectSuite = list("0000000000000")
    strValue = ["2","3","4","5","6","7","8","9","10","J","Q","K","A"]
    for i in range(len(hand)):
        vectSuite[strValue.index(hand[i].v)] = "1"
    vectSuite = ''.join(vectSuite)
    if "11111" in vectSuite:
        flagSuite = True
        index = vectSuite.rfind("11111")
        highCard = strValue[index]
        vect = []
        for i in range(5):
            indexTmp = index+4-i
            for j in range(len(hand)):
                if strValue[indexTmp] == hand[j].v:
                    vect.append(hand[j])
                    break
        highCard = vect[0].v
    else:
        vect = []
        highCard = "none"
    return flagSuite,highCard,vect

def getNbCardPerCombo(combo):
    order = ["none","pair","double pair","brelan","suite","color","full","carre","quinte flush"]
    nbCard = [0,2,4,3,5,5,5,4,5]
    return nbCard[order.index(combo)]
        
    
def winnerTest(cardsJ1,cardsJ2,verbose=False):
    comboJ1,highCardJ1,handSelectedJ1 = getBestHand(cardsJ1)
    comboJ2,highCardJ2,handSelectedJ2 = getBestHand(cardsJ2)
    if verbose == True:
        print("J1:")
        printDeck(cardsJ1)
        print("Combo:",comboJ1,"highCard:",highCardJ1)
        # printDeck(handSelectedJ1)
        print("")
        print("J2:")
        printDeck(cardsJ2)
        print("Combo:",comboJ2,"highCard:",highCardJ2)
        # printDeck(handSelectedJ2)
        print("")
    order = ["none","pair","double pair","brelan","suite","color","full","carre","quinte flush"]
    idxJ1 = order.index(comboJ1)
    idxJ2 = order.index(comboJ2)
    if idxJ1 > idxJ2:
        playerWinnerId = 1
    elif idxJ1 < idxJ2:
        playerWinnerId = 2
    else:
        playerWinnerId = 0

    if playerWinnerId == 0:
        orderValue = ["2","3","4","5","6","7","8","9","10","J","Q","K","A"]
        if comboJ1 != "double pair" and comboJ1 != "full":
            highCardJ1 = [highCardJ1]
            highCardJ2 = [highCardJ2]
        idxJ1 = orderValue.index(highCardJ1[0])
        idxJ2 = orderValue.index(highCardJ2[0])
        if idxJ1 > idxJ2:
            playerWinnerId = 1
        elif idxJ1 < idxJ2:
            playerWinnerId = 2
        else:
            if comboJ1 == "double pair" or comboJ1 == "full":
                idxJ1 = orderValue.index(highCardJ1[1])
                idxJ2 = orderValue.index(highCardJ2[1])
                if idxJ1 > idxJ2:
                    playerWinnerId = 1
                elif idxJ1 < idxJ2:
                    playerWinnerId = 2
                else:
                    playerWinnerId = 0
            else:
                playerWinnerId = 0
                
    if playerWinnerId == 0:
        nbCardsComboJ1 = getNbCardPerCombo(comboJ1)
        cardsLeftJ1 = sortDeckHighCard(handSelectedJ1[nbCardsComboJ1:5])
        nbCardsComboJ2 = getNbCardPerCombo(comboJ2)
        cardsLeftJ2 = sortDeckHighCard(handSelectedJ2[nbCardsComboJ2:5])
        for i in range(len(cardsLeftJ1)):
            idxJ1 = orderValue.index(cardsLeftJ1[i].v)
            idxJ2 = orderValue.index(cardsLeftJ2[i].v)
            if idxJ1 > idxJ2:
                playerWinnerId = 1
                break
            elif idxJ1 < idxJ2:
                playerWinnerId = 2
                break
            else:
                playerWinnerId = 0
            
    if verbose == True:
        if playerWinnerId == 1:
            print("J1 won")
        elif playerWinnerId == 2:
            print("J2 won")
        else:
            print("equality")

    return playerWinnerId
    
def decision(cardsJ1,cardsJ2,nbPlayer,nbRunToTest,aggresivity=0,verbose=False):
    """
    Parameters
    ----------
    cardsJ1 : list
        Cards J1. e.g: ["6h","Kd"]
    cardsJ2 : list
        Cards J1.
    nbPlayer : int
        Number of player.
    nbRunToTest : int
        Number of simulation. The higher, the more accurate it is, but the more time it takes.
    aggresivity : float between 0 and 1, optional
        Define how aggressive is gonna be the algo. The default is 0.
    verbose : bool, optional
        Show more info. The default is False.

    Returns
    -------
    decision : string
        Return the action to do.

    """
    nbCardTotal = 7
    
    nbWinJ1 = 0
    nbWinJ2 = 0
    
    deckInit = generateDeck()
    deckInit = removeCardFromDeck(deckInit,cardsJ1)
    deckInit = removeCardFromDeck(deckInit,cardsJ2)
    
    for j in range(nbRunToTest):
        deck = deckInit
        
        cardsJ1tmp,deck = completeHandWithRandomcards(nbCardTotal,cardsJ1,deck)
        cardsJ2tmp,deck = completeHandWithRandomcards(nbCardTotal,cardsJ2,deck)
        
        playerWinnerId = winnerTest(cardsJ1tmp,cardsJ2tmp,verbose=False)
        if playerWinnerId == 1:
            nbWinJ1 += 1
        elif playerWinnerId == 2:
            nbWinJ2 += 1
        else:
            pass
            
    chance = nbWinJ1/(nbWinJ1+nbWinJ2)
    limitFollow = chance + (1-chance)*aggresivity
    limitNbPlayer = 1-1/nbPlayer
    
    if limitFollow > limitNbPlayer:
        decision = "follow"
    else:
        decision = "quit"
    
    if verbose == True:
        print("nbWinJ1:",nbWinJ1)
        printDeck(cardsJ1)
        print("nbWinJ2:",nbWinJ2)
        printDeck(cardsJ2)
        print("Purcentage of chance of winning:",chance)
        print("Limite Follow:",limitFollow)
        print("Limite nb players:",limitNbPlayer)
        print("Decision:",decision)
        
    return decision,chance,limitNbPlayer

    
if __name__ == "__main__":
    
    
    nbPlayer = 3
    aggressivity = 0 #from 0 to 1
    nbRunToTest = 10000
    
    cardsJ1 = genrateHandFromStrList(["6h","Kd"])
    cardsJ2 = genrateHandFromStrList(["4h","8d"])

    decision(cardsJ1,cardsJ2,nbPlayer,nbRunToTest,verbose=True)







