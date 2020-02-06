# -*- coding: utf-8 -*-
"""
Created on Sat Dec 28 00:38:00 2019

@author: Charly

"""

import cv2
import numpy as np
import pytesseract
from sys import platform
if platform == "win32":
    pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
# from PIL import Image
from sklearn.cluster import KMeans
import copy
import math
import matplotlib.pyplot as plt
from PIL import Image
import scipy.cluster.hierarchy as hcluster
from difflib import SequenceMatcher
import time
import os

def listdir_fullpath(d):
    return [os.path.join(d, f) for f in os.listdir(d)]


"""time_start = time.clock()
time_elapsed = (time.clock() - time_start)"""

glbPlayerName = "tobamai"

class Player():
    def __init__(self,index,name,nbCoinHand,cxP,cyP,w,h,cxT,cyT):
        self.index = index
        self.name = name
        self.nbCoinHand = nbCoinHand
        self.cxP = int(cxP)     #info player position
        self.cyP = int(cyP)
        self.cxT = int(cxT)     #table position
        self.cyT = int(cyT)
        self.w = int(w)         #size info player
        self.h = int(h)
        self.role = "player"
        self.cxB = int(self.cxT + (self.cxP-self.cxT)/100*66)       #coin bet position
        self.cyB = int(self.cyT + (self.cyP-self.cyT)/100*66)
        self.deltaBx = 30
        self.deltaBy = 30
        self.lastAction = ""
        
    def showInfo(self):
        print("Player ",self.index," :")
        print("Name:",self.name,",nbCoinHand:",self.nbCoinHand,",nbCoinTable:",self.nbCoinTable,",role:",self.role,",lastAction:",self.lastAction)
        print("")
        
    def setIndex(self,index):
        self.index = index
        
    def setRole(self,role): #"player" orr "dealer"
        self.role = role
        
    def setNbCoinTable(self,nbCoinTable):
        self.nbCoinTable = nbCoinTable
        
    def setLastAction(self,lastAction):
        self.lastAction = lastAction
        
class Card():
    def __init__(self,val,fam):
        self.val = val
        self.fam = fam
        
    def showCards(self):
        print(self.val,self.fam)

        
        
def setNewDealer(listPlayer,index):
    for i in range(len(listPlayer)):
        if i == index:
            listPlayer[i].setRole("dealer")
        else:
            listPlayer[i].setRole("player")
    return listPlayer
        

def findWindow(large_image,verbose=False):
    
    # Read the images from the file
    small_image = cv2.imread('img/house.png')
    smallBottom_image = cv2.imread('img/smiley.png')
    
    result = cv2.matchTemplate(large_image,small_image, cv2.TM_CCOEFF_NORMED)
    resultBot = cv2.matchTemplate(large_image,smallBottom_image, cv2.TM_CCOEFF_NORMED)
    locTup = np.where(result >= 0.99)
    loc = np.transpose(np.array(locTup))
    
    if verbose == True:
        locBotTup = np.where(resultBot >= 0.99)
        cpWindow = copy.copy(large_image)
        w, h = small_image.shape[:-1]
        for pt in zip(*locTup[::-1]):  # Switch collumns and rows
            cv2.rectangle(cpWindow,  (pt[0], pt[1]), (pt[0] + h, pt[1] + w), (0, 0, 255), 2)
        w, h = smallBottom_image.shape[:-1]
        for pt in zip(*locBotTup[::-1]):  # Switch collumns and rows
            cv2.rectangle(cpWindow,  (pt[0], pt[1]), (pt[0] + h, pt[1] - w), (0, 100, 255), 2)
        showImg(cpWindow)

    
    if loc.shape[0] == 1:
        # We want the minimum squared difference
        mn,_,_,mnLoc = cv2.minMaxLoc(result)
        mn,_,_,mnLocBot = cv2.minMaxLoc(resultBot)
        
        # Draw the rectangle:
        # Extract the coordinates of our best match
        MPx,MPy = mnLoc
        MPxBot,MPyBot = mnLocBot
        
        # Step 2: Get the size of the template. This is the same size as the match.
        wTop,hTop = small_image.shape[:2]
        wBot,hBot = smallBottom_image.shape[:2]
        
        # Step 3: Draw the rectangle on large_image
        #cv2.rectangle(large_image, (MPx,MPy),(MPxBot+tcols,MPyBot+trows),(0,0,255),2)
        outputImg = large_image[MPy:MPyBot+wBot, MPx:MPxBot+hBot,:]

    else:
        outputImg = []
        MPx = 0
        MPy = 0
    return outputImg,MPx,MPy

def getNbPlayerV2(window,template):
    tmp = getLocTemplateInImage(window,template,threshold=0.95,grouping=True,verbose=False)
    return len(tmp)

def detectPlayers(window,stateGame,verbose=False):
    # nbPlayer = getNbPlayer(window)
    
    # windowFiltered = filterColor(window,rgb=[255,255,255],delta=0)
    windowFiltered = filterColorV2(window,[0,0,255],[10,255,255])
    im = Image.fromarray(np.flip(windowFiltered,2))
    im.save("img/tmp.png")

    template = cv2.imread('img/filteredPlayerBoxV3black.png')
    deltaW = 20
    w, h = template.shape[:-1]
    h = h+2*deltaW
    
    nbPlayer = getNbPlayerV2(windowFiltered,template)
    
    res = cv2.matchTemplate(windowFiltered, template, cv2.TM_CCOEFF_NORMED)
    threshold = 0.97                     
    loc = np.where(res >= threshold)
    loc = removeCloseCoor(np.transpose(np.array(loc)),nbPlayer)
    loc = (loc[0],loc[1]-deltaW)
    if verbose == True:
        cpWindow = copy.copy(window)
        for pt in zip(*loc[::-1]):  # Switch collumns and rows
            cv2.rectangle(cpWindow,  (pt[0], pt[1]), (pt[0] + h, pt[1] + w), (0, 0, 255), 2)
            # cv2.rectangle(window,  (pt[0], pt[1]), (pt[0] + h, pt[1] - w), (0, 100, 255), 2)
        showImg(cpWindow)
        showImg(windowFiltered)

    cxT = 333
    cyT = 237
        
    name,nbCoin = readNbPoints(window,loc,w,h)
    listPlayer = []
    i=0
    for pt in zip(*loc[::-1]):
        listPlayer.append(Player(i,name[i],nbCoin[i],pt[0]+h/2,pt[1]+w/2,w,h,cxT,cyT))
        i+=1
    
    argOrderPlayers = getOrderPlayers(loc,[cxT,cyT])
    
    listPlayer = [listPlayer[i] for i in argOrderPlayers]
    for i in range(len(listPlayer)):
        listPlayer[i].setIndex(i)
        
    listPlayer = readNbCoinTable(window,listPlayer)
    idxDealer = getDealerIndex(window,listPlayer)
    listPlayer = setNewDealer(listPlayer,idxDealer)
    listPlayer = guessLastActionsPlayers(listPlayer,stateGame)
    return window,listPlayer

def guessLastActionsPlayers(listPlayer,stateGame):
    for i in range(len(listPlayer)):
        if listPlayer[i].role == "dealer":
            index = i
            break
    print(index)
    for i in range(len(listPlayer)):
        idxPlayer = (i+index)%len(listPlayer)
        idxPlayerPrev = (i-1+index)%len(listPlayer)
        deltaNbCoinTable = listPlayer[idxPlayer].nbCoinTable - listPlayer[idxPlayerPrev].nbCoinTable
        if listPlayer[idxPlayer].name == glbPlayerName:
            actionTmp == " "
        elif stateGame == "begining" and (i == 1 or i==2):
            actionTmp = "call"
        else:
            if deltaNbCoinTable > 0.0001:
                actionTmp = "raised"
            elif deltaNbCoinTable < -0.0001:
                actionTmp = "fold"
            else:
                actionTmp = "call"
        listPlayer[idxPlayer].setLastAction(actionTmp)
    return listPlayer

def isfloat(value):
  try:
    float(value)
    return True
  except ValueError:
    return False

def readNbCoinTable(window,listPlayer):
    for i in range(len(listPlayer)):
        imgTmp = window[listPlayer[i].cyB-listPlayer[i].deltaBy:listPlayer[i].cyB+listPlayer[i].deltaBy,listPlayer[i].cxB-listPlayer[i].deltaBx:listPlayer[i].cxB+listPlayer[i].deltaBx,:]
        imgTmp = filterColor(imgTmp,rgb=[239,192,1],delta=80)
        kernel = np.ones((2,2), np.uint8) 
        imgTmp = cv2.erode(imgTmp, kernel, iterations=1) 
        showImg(imgTmp)
        # nbCoinT = pytesseract.image_to_string(imgTmp)
        nbCoinT = pytesseract.image_to_string(imgTmp, config="-c tessedit_char_whitelist=:0123456789 --psm 7")
        if len(nbCoinT)>=2 and nbCoinT[0] == "0":
            nbCoinT= nbCoinT[0]+"."+nbCoinT[1:]
        if nbCoinT == '':
            nbCoinT = "0"
        nbCoinT = nbCoinT.replace(",",".")
        if isfloat(nbCoinT):
            listPlayer[i].setNbCoinTable(float(nbCoinT))
        else:
            listPlayer[i].setNbCoinTable(0)
            print("Warning: during reading of coin table player ", listPlayer[i].name,", nb coin detected: ",nbCoinT)
    return listPlayer

def readMyCards(window,listPlayer,verbose=False):
    flagPlayerNameDetected = False
    for i in range(len(listPlayer)):
        if listPlayer[i].name == glbPlayerName:
            x1 = listPlayer[i].cxP-36
            x2 = listPlayer[i].cxP-16
            x3 = listPlayer[i].cxP+4
            y1 = listPlayer[i].cyP-60
            y2 = listPlayer[i].cyP-38
            y3 = listPlayer[i].cyP-22
            imgNum1 = window[y1:y2,x1:x2,:]
            imgType1 = window[y2:y3,x1:x2,:]
            imgNum2 = window[y1:y2,x2:x3,:]
            imgType2 = window[y2:y3,x2:x3,:]
            card1 = readCard(imgNum1,imgType1,verbose=verbose)
            card2 = readCard(imgNum2,imgType2,verbose=verbose)
            flagPlayerNameDetected = True
            
    if flagPlayerNameDetected == True:
        if card1 != [] and card2 != []:
            myCards = [card1,card2]
        else:
            myCards = []
    else:
        raise Exception("Error: no player called " + glbPlayerName + " detected")
    
    return myCards

            
def readCard(imgNumber,imgType,verbose=False):
    flagError = False
    vectType = ["h","d","c","s"]
    vectVal = ['A','K','Q','J','10','9','8','7','6','5','4','3','2']
    
    #try to read value from card
    cardValPsm7 = pytesseract.image_to_string(imgNumber,config='--psm 7')
    cardValPsm8 = pytesseract.image_to_string(imgNumber,config='--psm 8')
    if cardValPsm8 in vectVal:
        cardVal = cardValPsm8
    else:
        cardVal = cardValPsm7
    
    if cardVal in ["0","QO","O",")"]:
        cardVal = "Q"
    elif cardVal in ["Jy"]:
        cardVal = "J"
    elif cardVal in ["T"]:
        cardVal = "7"
    elif cardVal == "1":
        cardVal = "A"
    if not cardVal in vectVal:
        print("Warning: wrong card value red: ",cardVal)
        cardVal = "-1"
        
    #try to read family from card
    threshold = 0.7
    filtH = filterColor(imgType,rgb=[178, 7, 27],delta=10) #h
    filtD = filterColor(imgType,rgb=[230, 45, 0],delta=10) #d
    filtC = filterColor(imgType,rgb=[64, 64, 64],delta=10) #c
    filtS = filterColor(imgType,rgb=[0, 0, 0],delta=10) #s
    # showImg(filtH)
    # showImg(filtD)
    # showImg(filtC)
    # showImg(filtS)
    vectNbType = np.array([np.sum(filtH), np.sum(filtD), np.sum(filtC), np.sum(filtS)])

    argmax = np.argmin(vectNbType)

    cardFam = vectType[argmax]

    if not cardVal in vectVal:
        flagError = True
        
    if verbose == True and flagError == True:
        print("Error during card reading")
        

    card = Card(cardVal,cardFam)

    
    if verbose == True:
        print("cardVal: ",cardVal,", cardFam: ",cardFam)
        showImg(imgNumber)
        showImg(imgType)
        # print("nbHearth: ",nbHearth,", nbCarreau: ",nbCarreau,", nbPique:",nbPique,", nbTrefle: ",nbTrefle)
        # print("Char red: ",cardVal)

    return card
    
# def filterCards(img):
#     imgTmpBlack = filterColor(img,rgb=[0,0,0],delta=80)
#     imgTmpRed = filterColor(img,rgb=[204,26,14],delta=50)
#     imgComb = imgTmpBlack & imgTmpRed
#     return imgComb

def getLocTemplateInImage(window,template,threshold=0.95,grouping=True,verbose=False):
    clusterThresh = 5
    res = cv2.matchTemplate(window, template, cv2.TM_CCOEFF_NORMED)
    w, h = template.shape[0:2]
    loc = np.where(res >= threshold)
    
    if grouping == True:
        nbCluster = findNbClusters(np.transpose(np.array(loc)),clusterThresh)
        if nbCluster > 0:
            loc = removeCloseCoor(np.transpose(np.array(loc)),nbCluster)
        else:
            loc = np.array([])
    
    if verbose == True:
        for pt in zip(*loc[::-1]):  # Switch collumns and rows
            cv2.rectangle(window,  (pt[0], pt[1]), (pt[0] + h, pt[1] + w), (0, 0, 255), 2)
        showImg(window)

    return np.transpose(np.array(loc))



def readNbPoints(window,loc,w,h):
    name = []
    nbCoin = []
    similarityPlayerName = []
    for pt in zip(*loc[::-1]):  # Switch collumns and rows
        imgTmp = window[pt[1]:pt[1]+w,pt[0]:pt[0]+h,:]
        imgTmpName = filterColor(imgTmp,rgb=[255,255,255],delta=80)
        nameTmp = pytesseract.image_to_string(imgTmpName, config='--psm 7')
        similarityPlayerName.append(SequenceMatcher(None, glbPlayerName, nameTmp).ratio())
        name.append(nameTmp)
        imgTmpNbCoin = filterColor(imgTmp,rgb=[255,204,98],delta=50)
        # nbCoinTmp = pytesseract.image_to_string(imgTmpNbCoin, config='--psm 7', lang='eng')
        
        nbCoinTmp = pytesseract.image_to_string(imgTmpNbCoin)
        
        
        if nbCoinTmp == '':
            nbCoinTmp = "0"
        

        # if isfloat(nbCoinT):
        #     listPlayer[i].setNbCoinTable(float(nbCoinT))
        # else:
        #     listPlayer[i].setNbCoinTable(0)
    
        nbCoinTmp = nbCoinTmp.replace(' ','')
        nbCoinTmp = nbCoinTmp.replace(",",".")
        if isfloat(nbCoinTmp):
            # nbCoinIntVect = re.findall(r'\d+',nbCoinTmp)[0]
            nbCoinIntVect = float(nbCoinTmp)
        else:
            nbCoinIntVect = 0
            print("Warning: during reading of nb point player. nb point detected: ",nbCoinTmp)
        
        nbCoin.append(float(nbCoinIntVect))

    argmax = np.argmax(similarityPlayerName)
    name[argmax] = glbPlayerName
    
    return name,nbCoin
        

def removeCloseCoor(X,nbPlayer):
    if X.shape[0] > 0:
        kmeans = KMeans(n_clusters=nbPlayer, random_state=0).fit(X)
        kmeans.labels_
        kmeans.predict([[0, 0], [1, 1]])   
        output = (kmeans.cluster_centers_[:,0].astype(int),kmeans.cluster_centers_[:,1].astype(int))
    else:
        output = (X[:,0],X[:,1])
    return output

    

def showImg(window):
    if len(window.shape) == 2:
        plt.imshow(window, cmap='gray')   # this colormap will display in black / white
        plt.show()
    else:
        window = np.flip(window,2)
        plt.imshow(window)   # this colormap will display in black / white
        plt.show()




def filterColor(img,rgb=[255,255,255],delta=0):
    rgb = np.flip(rgb)
    imgCp = copy.copy(img[:,:,:])
    for i in range(img.shape[0]):
        for j in range(img.shape[1]):
            if img[i,j,0] >= rgb[0]-delta and img[i,j,0] <= rgb[0]+delta and img[i,j,1] >= rgb[1]-delta and img[i,j,1] <= rgb[1]+delta and img[i,j,2] >= rgb[2]-delta and img[i,j,2] <= rgb[2]+delta :
                imgCp[i,j,:] = [0,0,0]
            else:
                imgCp[i,j,:] = [255,255,255]
    return imgCp


def getCoordinateSmallImg(small_image,large_image,verbose=False):
    # method = cv2.TM_SQDIFF_NORMED
    # method = cv2.TM_CCOEFF_NORMED
    
    # Read the images from the file
    # small_image = cv2.imread('small.png')
    # large_image = cv2.imread('test.png')
    width, height = small_image.shape[:-1]
    
    result = cv2.matchTemplate(small_image, large_image, cv2.TM_SQDIFF_NORMED)
    
    # We want the minimum squared difference
    mn,_,mnLoc,_ = cv2.minMaxLoc(result)
    
    # Draw the rectangle:
    # Extract the coordinates of our best match
    MPx,MPy = mnLoc
    
    if verbose == True:
        imgCopy = copy.copy(large_image)
        cv2.rectangle(imgCopy,  (MPx, MPy), (MPx + height, MPy + width), (0, 0, 255), 2)
        showImg(large_image)
    return MPx,MPy,width,height

def getNbPlayer(window):
    posImg = cv2.imread("img/pos.png")
    MPx,MPy,width,height = getCoordinateSmallImg(posImg,window,verbose=False)
    posExtand = window[MPy:MPy+width,MPx:MPx+height+40,:]
    
    # showImg(posExtand)
    
    img = filterColor(posExtand,rgb=[255,255,255],delta=35)
    text = pytesseract.image_to_string(img, config='--psm 7')
    
    tmp1 = text.find('/')
    # tmp2 = text.find('(')
    
    return int(text[tmp1+1:tmp1+2])
    
    
def getOrderPlayers(loc,tableCenter):
    angle = []
    for pt in zip(*loc[::-1]):
        angle.append(math.atan2(-pt[0]+tableCenter[0],pt[1]-tableCenter[1])+np.pi)
    return np.argsort(angle)

def getDealerIndex(window,listPlayer):
    small_image = cv2.imread("img/dealerCoin.png")
    MPx,MPy,width,height = getCoordinateSmallImg(small_image,window)
    centerX = MPx+width/2
    centerY = MPy+height/2
    dist = []
    for i in range(len(listPlayer)):
        centerXp = listPlayer[i].cxP
        centerYp = listPlayer[i].cyP
        dist.append(math.sqrt((centerXp-centerX)**2+(centerYp-centerY)**2))
    return np.argmin(dist)

def isMyTurn(window):
    vectActOut,vectLocOut = detectPossibleActions(window)
    if len(vectActOut) >= 1:
        out = True
    else:
        out = False
    return out

def printListPlayer(listPlayer):
    for i in range(len(listPlayer)):
        listPlayer[i].showInfo()
        
def filterColorV2(img,l1,l2,verbose=False):     #l1 and l2 in hsv color
    l1 = np.asarray(l1)
    l2 = np.asarray(l2)
    img_hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    
    mask = cv2.inRange(img_hsv, l1, l2)
    
    backtorgb = cv2.cvtColor(mask,cv2.COLOR_GRAY2RGB)
    
    if verbose == True:
        showImg(backtorgb)
    
    return backtorgb
    
def findNbClusters(data,thresh):
    # clustering
    if data.shape[0] == 0:
        nbCluster = 0
    elif data.shape[0] == 1:
        nbCluster = 1
    else:
        clusters = hcluster.fclusterdata(data, thresh, criterion="distance")
        nbCluster = len(set(clusters))

    return nbCluster
        
def detectCards(window,verbose=False):
    filtCard = filterColorV2(window,[50, 0, 0],[100, 240, 240],verbose=False)
    template = cv2.imread("img/blackCard.png")
    
    loc = getLocTemplateInImage(filtCard,template,threshold=0.8,verbose=verbose)
    if len(loc.shape) == 2:
        newOrder = np.argsort(loc[:,1])
        loc = loc[newOrder]
    nbCardTable = loc.shape[0]
    wT,hT = template.shape[:2]
    cards = []
    for i in range(nbCardTable):
        imgTmp = window[loc[i,0]:loc[i,0]+wT,loc[i,1]:loc[i,1]+hT,:]
        imgTmpVal = imgTmp[7:32,5:30,:]
        # imgTmpVal = filterColor(imgTmpVal,rgb=[0,0,0],delta=230)
        imgTmpFam = imgTmp[30:54,5:27,:]
        cards.append(readCard(imgTmpVal,imgTmpFam,verbose=verbose))
        
    if verbose == True:
        print("Number of card detected on the table: ",nbCardTable)
        for i in range(len(cards)):
            cards[i].showCards()
        
    return cards

def detectPossibleActions(window):
    fileNames = ["img/actMiser.png","img/actParole.png","img/actPasser.png","img/actRelancer.png","img/actSuivre.png"]
    actionList = ["bet","call","fold","raise","follow"]
    vectActOut = []
    vectLocOut = []
    for i in range(len(fileNames)):
        template = cv2.imread(fileNames[i])
        tmp = getLocTemplateInImage(window,template,threshold=0.9,grouping=True,verbose=False)
        # tmp = matchTemplateScaleMe(window,template)
        if len(tmp) != 0:
            vectActOut.append(actionList[i])
            vectLocOut.append([tmp[0][0]+int(template.shape[0]/2),tmp[0][1]+int(template.shape[1]/2)])
    return vectActOut,vectLocOut


def getPot(window,potTotal=False):
    if potTotal == True:
        template = cv2.imread("img/potTotal.png")
    else:
        template = cv2.imread("img/pot.png")
    loc = getLocTemplateInImage(window,template,threshold=0.95,grouping=True,verbose=False)
    if len(loc) >= 1:
        x = loc[0][0]-2
        y = loc[0][1]+template.shape[1]
        potImg = window[x:x+template.shape[0]+4,y:y+60,:]
        if potTotal == True:
            potImg = filterColor(potImg,rgb=[255,255,255],delta=120)
        else:
            potImg = filterColor(potImg,rgb=[239,192,1],delta=80)
        kernel = np.ones((2,2), np.uint8) 
        potImg = cv2.erode(potImg, kernel, iterations=1) 
        nbCoinPot = pytesseract.image_to_string(potImg, config="-c tessedit_char_whitelist=.,0123456789 --psm 6")
        
        
        if len(nbCoinPot)>=2 and nbCoinPot[0] == "0" and nbCoinPot[1] != ".":
            nbCoinPot= nbCoinPot[0]+"."+nbCoinPot[1:]
        if nbCoinPot == '':
            nbCoinPot = "0"
        nbCoinPot = nbCoinPot.replace(",",".")
        if isfloat(nbCoinPot):
            nbCoinPot = float(nbCoinPot)
        else:
            nbCoinPot = 0
    else:
        nbCoinPot = 0
    
    return nbCoinPot

def getNbCoinFollow(window):
    template = cv2.imread("img/actSuivre.png")
    loc = getLocTemplateInImage(window,template,threshold=0.9,grouping=True,verbose=False)
    if len(loc) >= 1:
        x = loc[0][0]-12
        y = loc[0][1]
        imgNbCoin = window[x:x+12,y:y+80,:]
        imgNbCoin = filterColor(imgNbCoin,rgb=[255,255,255],delta=120)
        showImg(imgNbCoin)
        nbCoin = pytesseract.image_to_string(imgNbCoin, config="-c tessedit_char_whitelist=.,0123456789 --psm 6")
        if nbCoin[-1] == ".":
            nbCoin = nbCoin[0:-2]
        nbCoin = float(nbCoin)
    else:
        nbCoin = 0
    return nbCoin

def getStateGame(nbCardTable):
    if nbCardTable == 0:
        stateName = "begining"
    elif nbCardTable == 3:
        stateName = "flop"
    elif nbCardTable == 4:
        stateName = "turn"
    elif nbCardTable == 5:
        stateName = "river"
    return stateName
    
        
if __name__ == "__main__":
    testLogFiles = False
    
    if testLogFiles == True:
        listImgFileName = listdir_fullpath("log/img/")
        idImageInit = 5
    else:
        listImgFileName = ['log/img/m200206_010442.png']
        idImageInit = 0
    
    
    for j in range(idImageInit,len(listImgFileName)):
        fileName = listImgFileName[j]
        time_start = time.process_time()
        screenshot = cv2.imread(fileName)
        # screenshot = cv2.imread('img/actions.png')
        window,MPx,MPy = findWindow(screenshot,verbose=False)
        if testLogFiles == True:
            print("\Analysis of the image no: ",j)
        showImg(window)
        
        
        if type(window).__name__ != "list":
            print("nbCoinToFollow: ",getNbCoinFollow(window))
            print("Pot: ",getPot(window,potTotal=False))
            print("Pot total: ", getPot(window,potTotal=True))
            
            cards = detectCards(window,verbose=False)
            stateGame = getStateGame(len(cards))
            print("\nCards Table:")
            for i in range(len(cards)):
                cards[i].showCards()
            
            windowDetectPlayers,listPlayer = detectPlayers(window,stateGame,verbose=False)
            print("Number of players: ",len(listPlayer))
            
            idxDealer = getDealerIndex(window,listPlayer)
            setNewDealer(listPlayer,idxDealer)
            
            printListPlayer(listPlayer)
            myCards = readMyCards(window,listPlayer,verbose=False)
            print("My cards:")
            
            if myCards != []:
                myCards[0].showCards()
                myCards[1].showCards()
            else:
                print("No card detected in your hand")
            

            
            
            flagMyTurn = isMyTurn(window)
            
            time_elapsed = (time.process_time() - time_start)
        else:
            raise Exception("Error: no poker window detected")
        print("Time execution: ",time_elapsed)
        
        if testLogFiles == True:
            input("Press Enter to continue...")