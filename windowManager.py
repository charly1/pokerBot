import pygetwindow as gw
import imageAnalysis as imgAn
import cv2
import pyautogui
from time import sleep
import numpy as np
import re

# gw.getAllWindows()
# gw.getWindowsWithTitle('Untitled')
# gw.getFocusedWindow()
# gw.getFocusedWindow().title
# gw.getWindowsAt(10, 10)

nameWinMenuWinamax = "Accès rapide"

class Window():
    def __init__(self,window,x,y):
        self.w = window
        self.x = x
        self.y = y
        
        
def newScreenShot():
    screenshot = np.array(pyautogui.screenshot())
    screenshot = np.flip(screenshot,2)
    windowObj = Window(screenshot,0,0)
    return windowObj

def extractWindowGame(verbose=False):
    screenshotObj = newScreenShot()
    window,MPx,MPy = imgAn.findWindow(screenshotObj.w,verbose=True)
    windowObj = Window(window,MPx,MPy)
    if verbose == True:
        imgAn.showImg(window)
    return windowObj

def getListAllWinName():
    return gw.getAllTitles()

def findGameWindowName():
    listName = getListAllWinName()
    name = ""
    for i in range(len(listName)):
        if "Holdem" in listName[i]:
            name = listName[i]
            break
    return name

def focusWin(windowName):
    focus = gw.getWindowsWithTitle(windowName)[0]
    focus.minimize()
    focus.maximize()
    focus.restore()
    
def quitGameTable():
    # nameWinGame = findGameWindowName()
    # if nameWinGame != "":
    # focusWin(nameWinGame)
    windowObj = extractWindowGame()
    sleep(1)
    clickOnButton("img/sabsenter.png",windowObj)
    sleep(3)
    windowObj = extractWindowGame()
    clickOnButton("img/quitter.png",windowObj)
    sleep(3)
    windowObj = extractWindowGame()
    clickOnButton("img/requitter.png",windowObj)
    sleep(3)
    
    
def joinGameTable():
    sleep(1)
    focusWin(nameWinMenuWinamax)
    sleep(1)
    screenshotObj = newScreenShot()
    clickOnButton("img/kickGame_HLHE_01_fakeMoney.png",screenshotObj,offSetClick=[0,40])
    flagLoading = True
    while flagLoading:
        sleep(2)
        screenshotObj = newScreenShot()
        template = cv2.imread("img/enAttente.png")
        pos = imgAn.getLocTemplateInImage(screenshotObj.w,template,threshold=0.95,grouping=True,verbose=False)
        if len(pos) == 0:
            flagLoading = False
    sleep(2)
    clickOnButton("img/confirmer.png",screenshotObj)
    
def switchAutoReBuy():
    windowObj = extractWindowGame(verbose=True)
    sleep(1)
    clickOnButton("img/autoReBuy.png",windowObj)

    
        
def clickOnButton(fileNameImgButton,windowObj,offSetClick=[0,0],threshold=0.95,debug=False):
    template = cv2.imread(fileNameImgButton)
    pos = imgAn.getLocTemplateInImage(windowObj.w,template,threshold=0.95,grouping=True,verbose=False)
    if len(pos) < 1:
        raise Exception("Error: button '",fileNameImgButton,"' not detected on image")
    clickY = windowObj.y+pos[0][0]+int(template.shape[0]/2)+offSetClick[1]
    clickX = windowObj.x+pos[0][1]+int(template.shape[1]/2)+offSetClick[0]
    if debug == False:
        pyautogui.click(clickX, clickY)
    else:
        pyautogui.moveTo(clickX, clickY)
    
def saveMoneyBySwitchingTable():
    quitGameTable()
    joinGameTable()
    switchAutoReBuy()
    
def extractBlindVal():
    strTmp = findGameWindowName()
    indexInit = strTmp.find("-")
    strTmp = strTmp[indexInit+1:-1]
    indexFinal = strTmp.find("/")
    newStr = strTmp[0:indexFinal]
    newStr = re.findall("\d+\,\d+",newStr)[0].replace(",",".")
    out = float(newStr)
    return out

def typeNumberFromKeyboard(val):
    strVal = "%.1f" % val
    for i in range(len(strVal)):
        pyautogui.press(strVal[i])

    
if __name__ == "__main__":
    # saveMoneyBySwitchingTable()
    # print()
    print(extractBlindVal())
    


