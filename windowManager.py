import pygetwindow as gw
import imageAnalysis as imgAn
import cv2
import pyautogui
from time import sleep
import numpy as np

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
    
def quitGameTable(windowObj):
    # nameWinGame = findGameWindowName()
    # if nameWinGame != "":
    # focusWin(nameWinGame)
    sleep(1)
    clickOnButton("img/sabsenter.png",windowObj)
    # sleep(1)
    # clickOnButton("img/quitter.png",windowObj)
    # sleep(1)
    # clickOnButton("img/requitter.png",windowObj)
    # focusWin(nameWinMenuWinamax)
        
        
def clickOnButton(fileNameImgButton,windowObj,debug=True):
    template = cv2.imread(fileNameImgButton)
    pos = imgAn.getLocTemplateInImage(windowObj.w,template,threshold=0.95,grouping=True,verbose=False)
    clickY = pos[0][0]
    clickX = pos[0][1]
    print(pos)
    if debug == False:
        pyautogui.click(windowObj.x+clickX, windowObj.y+clickY)
    else:
        pyautogui.move(windowObj.x, windowObj.y)
    

if __name__ == "__main__":
    # screenshot = cv2.imread("log/img/m200206_230041.png")
    screenshot = np.array(pyautogui.screenshot())
    screenshot = np.flip(screenshot,2)
    imgAn.showImg(screenshot)
    window,MPx,MPy = imgAn.findWindow(screenshot,verbose=True)
    imgAn.showImg(window)
    windowObj = Window(window,MPx,MPy)
    quitGameTable(windowObj)
    # winamaxMenuWinName = gw.getWindowsWithTitle('Accès rapide')[0]
    # focusWin(winamaxMenuWinName)

