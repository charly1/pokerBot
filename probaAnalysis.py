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
import pickle
import time

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
            raise Exception("Error: ",strCard[0]," is not a valid value for",strCard)
        return value
    
    def extractFamily(self,strCard):
        strCmp = "shdc"
        if strCard[-1] in strCmp:
            value = strCard[-1]
        else:
            value = -1
            raise Exception("Error: ",strCard[-1]," is not a valid family for ",strCard)
        return value
    
def genrateHandFromStrList(listStrCardsCp):
    listStrCards = copy.copy(listStrCardsCp)
    for i in range(len(listStrCards)):
        listStrCards[i] = Card(listStrCards[i])
    return listStrCards
    
def printDeck(deck):
    for i in range(len(deck)):
        print(deck[i].v,deck[i].f)
    
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
        flagCardFound = False
        for i in range(len(deck)):
            if deck[i].v == card[j].v and deck[i].f == card[j].f:
                deck.remove(deck[i])
                flagCardFound = True
                break
        if flagCardFound == False:
            raise Exception("Error: crads in double has been found in the hand or on the table")
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
    # strValue = ["2","3","4","5","6","7","8","9","10","J","Q","K","A"]
    strValue = ["A","K","Q","J","10","9","8","7","6","5","4","3","2"]
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
        if strValue.index(highCard) > strValue.index(lowCard):
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
    elif vectSuite[0:4] == "1111" and vectSuite[12] == "1":
        flagSuite = True
        highCard = "5"
        indexVect = [12,0,1,2,3]
        vect = []
        for indexTmp in indexVect:
            for j in range(len(hand)):
                if strValue[indexTmp] == hand[j].v:
                    vect.append(hand[j])
                    break
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
        print("J2:")
        printDeck(cardsJ2)
        print("Combo:",comboJ2,"highCard:",highCardJ2)
        # printDeck(handSelectedJ2)
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
        print("")
        
    dictInfoCombo = {"comboJ1":comboJ1,
                     "comboJ2":comboJ2,
                     "highCardJ1":highCardJ1,
                     "highCardJ2":highCardJ2,
                     "playerWinnerId":playerWinnerId}

    return playerWinnerId,dictInfoCombo
    
def decision(cardsAllP,cardsTable,nbRunToTest,aggresivity=0,verbose=False):
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
    nbCardTableMax = 5
    nbCardHandMax = 2
    
    nbPlayer = len(cardsAllP)
    
    nbWinJ1 = 0
    nbWinJ2 = 0
    
    nbWinP1 = 0
    nbWinOtherP = 0
    
    deckInit = generateDeck()
    for i in range(nbPlayer):
        deckInit = removeCardFromDeck(deckInit,cardsAllP[i])
    deckInit = removeCardFromDeck(deckInit,cardsTable)
    
    for j in range(nbRunToTest):
        deck = deckInit
        
        cardsTableCompleted,deck = completeHandWithRandomcards(nbCardTableMax,cardsTable,deck)
        
        cardsAllPcompleted = []
        for i in range(nbPlayer):
            cardsTmp = cardsAllP[i]+cardsTableCompleted
            cardsTmp,deck = completeHandWithRandomcards(nbCardTotal,cardsTmp,deck)
            cardsAllPcompleted.append(cardsTmp)
        
        idPlayerToTest = 0
        flagP1win = True
        for i in range(nbPlayer):
            if i != idPlayerToTest:
                playerWinnerId,dictInfoCombo = winnerTest(cardsAllPcompleted[idPlayerToTest],cardsAllPcompleted[i],verbose=False)
                if playerWinnerId == 2:
                    flagP1win = False
                    break
        
        if flagP1win == True:
            nbWinP1 += 1
        else:
            nbWinOtherP += 1

    chance = nbWinP1/(nbWinP1+nbWinOtherP)
    limitFollow = chance
    limitNbPlayer = 1/nbPlayer
    
    if limitFollow > 0.98:
        decision = ["raise","bet"]
        raiseFactorPot = 100000000
    elif limitFollow > limitNbPlayer+0.4+aggresivity:
        decision = ["raise","bet"]
        raiseFactorPot = 20
    if limitFollow > limitNbPlayer+0.2+aggresivity:
        decision = ["bet","follow"]
        raiseFactorPot = 2
    elif limitFollow > limitNbPlayer:
        decision = ["call","follow"]
        raiseFactorPot = 0
    else:
        decision = ["call","fold"]
        raiseFactorPot = 0
    
    if verbose == True:
        printDeck(cardsAllPcompleted[idPlayerToTest])
        print("Nb win P1: ",nbWinP1)
        print("Nb win others: ",nbWinOtherP)
        print("Purcentage of chance of winning:",chance)
        print("Limite Follow:",limitFollow)
        print("Limite nb players:",limitNbPlayer)
        print("Decision:",decision)
        
    return decision,chance,limitNbPlayer,raiseFactorPot,dictInfoCombo

def findBestNbRunForStdDevMax(cardsJ1,cardsTable,stdDevMax,nbRunInit):
    vectChance = []
    stdDev = 10000
    nbRunStepCoef = 1.5
    nbRunOpptimum = nbRunInit
    while stdDev > stdDevMax:
        vectChance = []
        for i in range(100):
            cardsJ1testVar = genrateHandFromStrList(["9h","8s"])
            cardsJ2 = genrateHandFromStrList([])
            cardsTable = genrateHandFromStrList([])
            cardsAllP = [cardsJ1testVar]
            for j in range(nbPlayer-1):
                cardsAllP.append(cardsJ2)
            _,chance,limitNbPlayer,_,_ = decision(cardsAllP,cardsTable,nbRunOpptimum,verbose=False)
            vectChance.append(chance)
            # print(chance)
            
        stdDev = np.std(vectChance)
        print("std:",stdDev)
        if stdDev > stdDevMax:
            nbRunOpptimum = int(nbRunOpptimum*nbRunStepCoef)
            print(nbRunOpptimum)
    
    return nbRunOpptimum

def saveData(your_content,varName):
    fileName = "data/"+varName
    with open(fileName, 'wb') as f:
        pickle.dump(your_content, f)
        
def loadData(varName):
    fileName = "data/"+varName
    with open(fileName, 'rb') as f:
        var_you_want_to_load_into = pickle.load(f)
    return var_you_want_to_load_into

def generateBucketsPreFlop(boolSaveData=False):
    strValue = ["2","3","4","5","6","7","8","9","10","J","Q","K","A"]
    strFamily = ["h","s"]
    nbPlayer = 2
    
    checkNbRun = 0
    listCardsTest = []
    for i in range(len(strValue)):
        for j in range(len(strFamily)-1):
            card1 = strValue[i]+strFamily[j]
            for k in range(len(strValue)):
                for l in range(len(strFamily)):
                    if not(i==k and j==l):
                        if i>=k:
                            checkNbRun += 1
                            card2 = strValue[k]+strFamily[l]
                            listCardsTest.append([card1,card2])
                            # print(card1,card2)
                        
    # nbRunToTest = findBestNbRunForStdDevMax(genrateHandFromStrList(["9h","8s"]),genrateHandFromStrList([]),0.01,3000)
    nbRunToTest = 10000
                        
    chanceVect = []
    for i in range(len(listCardsTest)):
        cardsJ1 = genrateHandFromStrList(listCardsTest[i])
        cardsJ2 = genrateHandFromStrList([])
        cardsTable = genrateHandFromStrList([])
        cardsAllP = [cardsJ1]
        for j in range(nbPlayer-1):
            cardsAllP.append(cardsJ2)
        
        _,chance,limitNbPlayer,_,_ = decision(cardsAllP,cardsTable,nbRunToTest,verbose=False)
        strCards = listCardsTest[i][0]+listCardsTest[i][1]
        chanceVect.append(chance)
        print(strCards,chance)
        
    argSort = np.argsort(chanceVect)
    listCardsTest = [listCardsTest[i] for i in argSort]
    chanceVect = [chanceVect[i] for i in argSort]
    
    if boolSaveData == True:
        dicSave = {"chanceVect":chanceVect,"listCardsTest":listCardsTest}
        saveData(dicSave,"bucketPreFlop")
        

                        
                        
    print("checkNbRun:",checkNbRun)
    
def getBucketIdPreflop(cards,verbose=False):
    #speed: 8000/s
    if len(cards)!=2:
        raise Exception("Error: wrong number of cards given to the bucket preflop calculator")
    strValue = ["2","3","4","5","6","7","8","9","10","J","Q","K","A"]
    
    dicSave = loadData("bucketPreFlop")
    chanceVect = dicSave["chanceVect"]
    listCardsTest = dicSave["listCardsTest"]
    # argSort = np.argsort(chanceVect)
    # listCardsTest = [listCardsTest[i] for i in argSort]
    # chanceVect = [chanceVect[i] for i in argSort]
    
    if strValue.index(cards[0].v) > strValue.index(cards[1].v):
        equivCard = [cards[0].v,cards[1].v]
    else:
        equivCard = [cards[1].v,cards[0].v]
    equivCard[0] += "h"
    if cards[0].f == cards[1].f:
        equivCard[1] += "h" 
    else:
        equivCard[1] += "s" 
    # equivCards = genrateHandFromStrList(equivCard1)
    flagCardFound = False
    for i in range(len(listCardsTest)):
        if (listCardsTest[i][0] == equivCard[0] and listCardsTest[i][1] == equivCard[1]) or (listCardsTest[i][0] == equivCard[1] and listCardsTest[i][1] == equivCard[0]):
            chance = chanceVect[i]
            indexTmp = i
            flagCardFound = True
            break
    if flagCardFound == False:
        raise Exception("Error: equivalence of card not found")
    rangeCard = indexTmp/len(listCardsTest)
    if verbose == True:
        print("chance:",chance,"rangeCard:",rangeCard)
    return chance,rangeCard

    
def testAlgo():
    parametersToTest = ["comboJ1","comboJ2","highCardJ1","highCardJ2","playerWinnerId"]
    test = []
    test.append({"cardsJ1":["2s","2h"],
                 "cardsJ2":["3s","10s"],
                 "cardsTable":["3h","10c","10h","Jc","8s"],
                 "comboJ1":"double pair",
                 "comboJ2":"full",
                 "highCardJ1":["10","2"],
                 "highCardJ2":["10","3"],
                 "playerWinnerId":2})
    
    test.append({"cardsJ1":["Qs","As"],
                 "cardsJ2":["Kd","Kc"],
                 "cardsTable":["3h","Ks","10s","Js","Kh"],
                 "comboJ1":"quinte flush",
                 "comboJ2":"carre",
                 "highCardJ1":"A",
                 "highCardJ2":"K",
                 "playerWinnerId":1})
    
    test.append({"cardsJ1":["Qs","Ah"],
                 "cardsJ2":["Kd","Qc"],
                 "cardsTable":["3h","Ks","10s","Js","Kh"],
                 "comboJ1":"suite",
                 "comboJ2":"brelan",
                 "highCardJ1":"A",
                 "highCardJ2":"K",
                 "playerWinnerId":1})
    
    flagError = False
    for i in range(len(test)):
        cardsJ1 = genrateHandFromStrList(test[i]["cardsJ1"])
        cardsJ2 = genrateHandFromStrList(test[i]["cardsJ2"])
        cardsTable = genrateHandFromStrList(test[i]["cardsTable"])
        cardsAllP = [cardsJ1]
        for j in range(nbPlayer-1):
            cardsAllP.append(cardsJ2)
        _,_,_,_,dictInfoCombo = decision(cardsAllP,cardsTable,nbRunToTest,verbose=False)
        for j in range(len(parametersToTest)):
            paramName = parametersToTest[j]
            if dictInfoCombo[paramName] != test[i][paramName]:
                flagError = True
                raise Exception("Error:",paramName," is not valid for test no:",i)
                break
    if flagError == False:
        print("Test passed successfully")
    
if __name__ == "__main__":
    
    nbPlayer = 2
    
    aggressivity = 0 #from 0 to 1
    nbRunToTest = 1
    
    # testAlgo()
    
    # generateBucketsPreFlop(boolSaveData=True)
    
    print(getBucketIdPreflop(genrateHandFromStrList(["4h","As"]),verbose=False))

    
    # cardsTable = genrateHandFromStrList(["2h","10c","10h","Jc","8s"])
    # cardsJ1 = genrateHandFromStrList(["2h","2s"])
    # cardsJ2 = genrateHandFromStrList([])
    # cardsAllP = [cardsJ1]
    # for i in range(nbPlayer-1):
    #     cardsAllP.append(cardsJ2)

    # decision(cardsAllP,cardsTable,nbRunToTest,verbose=False)
    

