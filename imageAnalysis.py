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
import click
import time
import re
import imutils
from PIL import Image

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
        
    def showInfo(self):
        print("Player ",self.index," :")
        print("Name:",self.name,",nbCoinHand:",self.nbCoinHand,",nbCoinTable:",self.nbCoinTable,",role:",self.role)
        print("")
        
    def setIndex(self,index):
        self.index = index
        
    def setRole(self,role): #"player" orr "dealer"
        self.role = role
        
    def setNbCoinTable(self,nbCoinTable):
        self.nbCoinTable = nbCoinTable
        
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

def detectPlayers(window,verbose=False):
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
        
    readNbCoinTable(window,listPlayer)
    return window,listPlayer

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
        nbCoinT = pytesseract.image_to_string(imgTmp)
        if nbCoinT == '':
            nbCoinT = "0"
        # print(listPlayer[i].name)
        # print(nbCoinT)
        # showImg(imgTmp)
        
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
    vectType = ["h","d","s","c"]
    vectVal = ['A','K','Q','J','10','9','8','7','6','5','4','3','2']
    cardVal = pytesseract.image_to_string(imgNumber,lang='eng', config='--psm 10')
    if cardVal == "O" or cardVal == "QO":
        cardVal = "Q"
    threshold = 0.8
    loc = getLocTemplateInImage(imgType,cv2.imread("img/hearthH.png"),grouping=False,threshold=threshold)
    nbHearth = loc.shape[0]
    loc = getLocTemplateInImage(imgType,cv2.imread("img/carreauH.png"),grouping=False,threshold=threshold)
    nbCarreau = loc.shape[0]
    loc = getLocTemplateInImage(imgType,cv2.imread("img/piqueH.png"),grouping=False,threshold=threshold)
    nbPique = loc.shape[0]
    loc = getLocTemplateInImage(imgType,cv2.imread("img/trefleH.png"),grouping=False,threshold=threshold)
    nbTrefle = loc.shape[0]
    # print("nbHearth:",nbHearth," nbCarreau:",nbCarreau,"nbPique: ",nbPique,"nbTrefle:",nbTrefle)
    vectNbType = np.array([nbHearth,nbCarreau,nbPique,nbTrefle])
    total = np.sum(vectNbType)
    argmax = np.argmax(vectNbType)
    if total >= 1:
        cardFam = vectType[argmax]
    else:
        flagError = True
        cardFam = "none"
    if not cardVal in vectVal:
        flagError = True
        
    if verbose == True and flagError == True:
        print("Error during card reading")
        
    if flagError == True:
        card = []
    else:
        card = Card(cardVal,cardFam)

    
    if verbose == True:
        print("cardVal: ",cardVal,", cardFam: ",cardFam)
        showImg(imgNumber)
        showImg(imgType)
        print("nbHearth: ",nbHearth,", nbCarreau: ",nbCarreau,", nbPique:",nbPique,", nbTrefle: ",nbTrefle)
        print("Char red: ",cardVal)

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
        
        nbCoinTmp = pytesseract.image_to_string(imgTmpNbCoin,config='--psm 10 --oem 3 -c tessedit_char_whitelist=0123456789')
        
        nbCoinTmp = nbCoinTmp.replace(' ','')
        if nbCoinTmp.isdigit():
            nbCoinIntVect = re.findall(r'\d+',nbCoinTmp)[0]
        else:
            nbCoinIntVect = 0
            print("Warning: during reading of nb point player. nb point detected: ",nbCoinTmp)
        
        nbCoin.append(int(nbCoinIntVect))

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
    
    loc = getLocTemplateInImage(filtCard,template,threshold=0.9,verbose=verbose)
    if len(loc.shape) == 2:
        newOrder = np.argsort(loc[:,1])
        loc = loc[newOrder]
    nbCardTable = loc.shape[0]
    wT,hT = template.shape[:2]
    cards = []
    for i in range(nbCardTable):
        imgTmp = window[loc[i,0]:loc[i,0]+wT,loc[i,1]:loc[i,1]+hT,:]
        imgTmpVal = filterColor(imgTmp[7:32,5:30,:],rgb=[0,0,0],delta=230)
        imgTmpFam = imgTmp[30:54,5:27,:]
        cards.append(readCard(imgTmpVal,imgTmpFam,verbose=False))
        
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




    
# def matchTemplateScaleMe(window,template):
#     # template = cv2.imread('template.jpg') # template image
#     # window = cv2.imread('image.jpg') # image
    
#     template = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
#     image = cv2.cvtColor(window, cv2.COLOR_BGR2GRAY)
    
#     loc = False
#     threshold = 0.9
#     w, h = template.shape[::-1]
#     for scale in np.linspace(0.2, 1.0, 20)[::-1]:
#         resized = imutils.resize(template, width = int(template.shape[1] * scale))
#         w, h = resized.shape[::-1]
#         res = cv2.matchTemplate(image,resized,cv2.TM_CCOEFF_NORMED)
    
#         loc = np.where( res >= threshold)
#         if len(zip(*loc[::-1])) > 0:
#             break
    
#     if loc and len(zip(*loc[::-1])) > 0:
#         for pt in zip(*loc[::-1]):
#             cv2.rectangle(window, pt, (pt[0] + w, pt[1] + h), (0,0,255), 2)
    
#     cv2.imshow('Matched Template', window)
#     cv2.waitKey(0)
#     cv2.destroyAllWindows()
    
#     return False

        
        
if __name__ == "__main__":
    
    
    time_start = time.process_time()
    screenshot = cv2.imread('img/last2.png')
    # screenshot = cv2.imread('img/actions.png')
    window,MPx,MPy = findWindow(screenshot,verbose=False)
    
    print(detectPossibleActions(window))
    
    
    if window != []:
        windowDetectPlayers,listPlayer = detectPlayers(window,verbose=False)
        print("Number of players: ",len(listPlayer))
        
        idxDealer = getDealerIndex(window,listPlayer)
        setNewDealer(listPlayer,idxDealer)
        
        printListPlayer(listPlayer)
        myCards = readMyCards(window,listPlayer)
        print("My cards:")
        
        if myCards != []:
            myCards[0].showCards()
            myCards[1].showCards()
        else:
            print("No card detected in your hand")
        
        cards = detectCards(window,verbose=False)
        
        flagMyTurn = isMyTurn(window)
        
        time_elapsed = (time.process_time() - time_start)
    else:
        raise Exception("Error: no poker window detected")
    print("Time execution: ",time_elapsed)