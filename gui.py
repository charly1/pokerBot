# -*- coding: utf-8 -*-
"""
Created on Sun Dec 29 17:36:23 2019

@author: Charly
"""

import tkinter as tk
import imageAnalysis as imgAn
import probaAnalysis as prbAn
import cv2
import numpy as np
import pyautogui
import threading
from PIL import Image
import pyautogui
import datetime
from time import sleep


def saveArrayToPng(filename,array):
    im = Image.fromarray(np.flip(array,axis=2))
    im.save(filename)
    
def getDateAsString():
    return datetime.datetime.now().strftime("%y%m%d_%H%M%S")



class AppPokerBot(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        self.parent = parent
        
        self.buttonState = False
        
        self.toggleActivity = tk.IntVar()
        self.toggleActivity.set(True)
        self.CBtoggleActivity = tk.Checkbutton(self.parent, text="Activity", variable=self.toggleActivity,state=tk.DISABLED)
        self.CBtoggleActivity.pack()
        
        self.boolIsMyTurn = tk.IntVar()
        self.boolIsMyTurn.set(False)
        self.CBboolIsMyTurn = tk.Checkbutton(self.parent, text="Is it my turn?", variable=self.boolIsMyTurn,state=tk.DISABLED)
        self.CBboolIsMyTurn.pack()
        
        self.boolTableDetected = tk.IntVar()
        self.boolTableDetected.set(False)
        self.CBboolIsTableDetected = tk.Checkbutton(self.parent, text="Is table detected?", variable=self.boolTableDetected,state=tk.DISABLED)
        self.CBboolIsTableDetected.pack()
        
        self.BoxParams = tk.LabelFrame(self.parent, text="Parameters", padx=2, pady=2)
        self.BoxParams.pack() 
        
        self.BoxCmd = tk.LabelFrame(self.BoxParams, text="Commands", padx=5, pady=5)
        self.BoxCmd.pack(side=tk.LEFT)   
        
        self.BoxSelectImgSource = tk.LabelFrame(self.BoxCmd, text="Image from", padx=3, pady=3)
        self.BoxSelectImgSource.pack()
        self.imgSource = tk.StringVar(self.BoxSelectImgSource)
        self.imgSource.set("Screen") # default value
        self.imgSource.trace('w',self.cbChangeImgSource)
        self.optionMenuReconstr = tk.OptionMenu(self.BoxSelectImgSource, self.imgSource, *["File","Screen"])
        self.optionMenuReconstr.pack(side=tk.LEFT)
        self.fileNameImgSource = tk.StringVar() 
        self.fileNameImgSource.set("img/test.png")
        self.entreeImgSource = tk.Entry(self.BoxSelectImgSource, textvariable=self.fileNameImgSource, width=20)
        self.entreeImgSource.pack(side=tk.RIGHT)
        if self.imgSource.get() == "Screen":
            self.entreeImgSource.config(state="disabled")
        
        # self.BoxSaveScreenShot = tk.LabelFrame(self.BoxCmd, text="Screenshot", padx=3, pady=3)
        # self.BoxSaveScreenShot.pack(fill="both", expand="yes")

        # self.fileNameScreenshot = tk.StringVar() 
        # self.fileNameScreenshot.set("img/screenshot.png")
        # self.entreeImgScreenshot = tk.Entry(self.BoxSaveScreenShot, textvariable=self.fileNameScreenshot, width=20)
        # self.entreeImgScreenshot.pack(side=tk.RIGHT)
        
        self.BoxRun = tk.LabelFrame(self.BoxCmd, text="Run", padx=3, pady=3)
        self.BoxRun.pack(fill="both", expand="yes")
        self.boutonStartBot=tk.Button(self.BoxRun, text="Start", command=self.cbStartBotBackGround)
        self.boutonStartBot.pack(padx=5, pady=5,side=tk.LEFT)
        self.toggleLoop = tk.IntVar()
        self.toggleLoop.set(False)
        self.CBtoggleLoop = tk.Checkbutton(self.BoxRun, text="Loop", variable=self.toggleLoop)
        self.CBtoggleLoop.pack(side=tk.RIGHT)
        
        self.boolEnableBotPlay = tk.IntVar()
        self.boolEnableBotPlay.set(True)
        self.CBboolEnableBotPlay = tk.Checkbutton(self.BoxCmd, text="Enable Bot Play", variable=self.boolEnableBotPlay)
        self.CBboolEnableBotPlay.pack()
        
        self.boutonSaveScreenShot=tk.Button(self.BoxCmd, text="Save Screenshot", command=self.cbSaveScreenshot)
        self.boutonSaveScreenShot.pack()
        self.boolEnableLogScreenShot = tk.IntVar()
        self.boolEnableLogScreenShot.set(False)
        self.CBboolEnableLogScreenShot = tk.Checkbutton(self.BoxCmd, text="Enable Log Screenshot", variable=self.boolEnableLogScreenShot)
        self.CBboolEnableLogScreenShot.pack()
        
        
        
        self.BoxProba = tk.LabelFrame(self.BoxParams, text="Probability computation", padx=3, pady=3)
        self.BoxProba.pack(side=tk.LEFT)
        
        self.BoxNbRunSim = tk.LabelFrame(self.BoxProba, text="Number of simulation", padx=3, pady=3)
        self.BoxNbRunSim.pack(fill="both", expand="yes")
        self.varSpinBoxNbRunSim = tk.StringVar(self.BoxNbRunSim)
        self.varSpinBoxNbRunSim.set("1000")
        self.spinBoxNbRunSim = tk.Spinbox(self.BoxNbRunSim, from_=0, to=10000,textvariable=self.varSpinBoxNbRunSim)
        self.spinBoxNbRunSim.pack()
        
        self.valAggressivity = tk.DoubleVar()
        self.valAggressivity.set(0.)
        self.scaleAggressivity = tk.Scale(self.BoxProba, variable=self.valAggressivity,orient='horizontal',from_=0, to=1,resolution=0.01,label='Aggressivity')
        self.scaleAggressivity.pack()
        
        self.BoxChanceOfWin = tk.LabelFrame(self.BoxProba, text="% of chance of winning", padx=3, pady=3)
        self.BoxChanceOfWin.pack(fill="both", expand="yes")
        self.valChanceOfWin = tk.StringVar()
        self.entreeChanceOfWin = tk.Entry(self.BoxChanceOfWin, textvariable=self.valChanceOfWin, width=20,state="disabled")
        self.entreeChanceOfWin.pack()
        
        self.BoxBetMax = tk.LabelFrame(self.BoxProba, text="bet max", padx=3, pady=3)
        self.BoxBetMax.pack(fill="both", expand="yes")
        self.valBetMax = tk.StringVar()
        self.entreeBetMax = tk.Entry(self.BoxBetMax, textvariable=self.valBetMax, width=20,state="disabled")
        self.entreeBetMax.pack()
        
        self.BoxLimitNbPlayer = tk.LabelFrame(self.BoxProba, text="Limit", padx=3, pady=3)
        self.BoxLimitNbPlayer.pack(fill="both", expand="yes")
        self.valLimitNbPlayer = tk.StringVar()
        self.entreeLimitNbPlayer = tk.Entry(self.BoxLimitNbPlayer, textvariable=self.valLimitNbPlayer, width=20,state="disabled")
        self.entreeLimitNbPlayer.pack()
        
        self.BoxAction = tk.LabelFrame(self.BoxProba, text="Action", padx=3, pady=3)
        self.BoxAction.pack(fill="both", expand="yes")
        self.valAction = tk.StringVar()
        self.entreeAction = tk.Entry(self.BoxAction, textvariable=self.valAction, width=20,state="disabled")
        self.entreeAction.pack()




        self.BoxInfos = tk.LabelFrame(self.parent, text="Info", padx=2, pady=2)
        self.BoxInfos.pack()
        
        self.BoxInfoPlayer = tk.LabelFrame(self.BoxInfos, text="Info Players:")
        self.BoxInfoPlayer.pack(side=tk.LEFT,fill=tk.BOTH)
        
        self.BoxNbPlayer = tk.LabelFrame(self.BoxInfoPlayer, text="Nb Player:")
        self.BoxNbPlayer.pack()
        self.nbPlayer = tk.StringVar()
        self.nbPlayer.set("")
        self.LabelNbPlayer = tk.Entry(self.BoxNbPlayer,textvariable = self.nbPlayer,width=10,state="disabled")
        self.LabelNbPlayer.pack(padx=2,pady=2)
        
        self.BoxAroundTabPlayers = tk.LabelFrame(self.BoxInfoPlayer, text="", relief=tk.FLAT)
        self.BoxAroundTabPlayers.pack()
        self.vectTitle = ["Name","Coin Hand","Coin Table","Dealer","Action"]
        self.nbPerson = 10
        self.nbTitleInfoPlayer = len(self.vectTitle)
        self.tab = []
        for row in range(self.nbPerson+1):
            tabTmp = []
            for col in range(self.nbTitleInfoPlayer):
                if row == 0:
                    vect = self.vectTitle
                else:
                    vect = [" "," "," "," "," "]
                labelTmp = tk.Label(self.BoxAroundTabPlayers, text=vect[col], borderwidth=2, relief=tk.GROOVE,width=10)
                tabTmp.append(labelTmp)
                labelTmp.grid(row=row, column=col)
            self.tab.append(tabTmp)
            
        self.BoxInfoCards = tk.LabelFrame(self.BoxInfos, text="Info Cards:", padx=2, pady=2)
        self.BoxInfoCards.pack(side=tk.LEFT,fill=tk.BOTH)
        

        
        self.BoxPotPotTotal = tk.LabelFrame(self.BoxInfoPlayer, text="", padx=2, pady=2,relief=tk.FLAT)
        self.BoxPotPotTotal.pack()
        self.BoxPot = tk.LabelFrame(self.BoxPotPotTotal, text="Pot", padx=2, pady=2)
        self.BoxPot.pack(side=tk.LEFT)
        self.valPot = tk.StringVar()
        self.entreePot = tk.Entry(self.BoxPot, textvariable=self.valPot, width=10,state="disabled")
        self.entreePot.pack(padx=2,pady=2)
        
        self.BoxPotTotal = tk.LabelFrame(self.BoxPotPotTotal, text="Pot Total", padx=2, pady=2)
        self.BoxPotTotal.pack(side=tk.LEFT)
        self.valPotTotal = tk.StringVar()
        self.entreePotTotal = tk.Entry(self.BoxPotTotal, textvariable=self.valPotTotal, width=10,state="disabled")
        self.entreePotTotal.pack(padx=2,pady=2)
        



        self.nbCardsTable = 5
        self.tabInfoGame = []
        
        self.BoxMyCard = tk.LabelFrame(self.BoxInfoCards, text="My Cards", padx=2, pady=2)
        self.BoxMyCard.pack()
        self.vectTitleInfoGame = ["Value","Family"]
        self.nbCardsMyHand = 2
        self.nbTitleInfoGame = len(self.vectTitleInfoGame)
        self.tabInfoMyHand = []
        for row in range(self.nbCardsMyHand+1):
            tabTmp = []
            for col in range(self.nbTitleInfoGame):
                if row == 0:
                    vect = self.vectTitleInfoGame
                else:
                    vect = [" "," "]
                labelTmp = tk.Label(self.BoxMyCard, text=vect[col], borderwidth=2, relief=tk.GROOVE,width=10)
                tabTmp.append(labelTmp)
                labelTmp.grid(row=row, column=col)
            self.tabInfoMyHand.append(tabTmp)
        
        self.BoxNbCardTable = tk.LabelFrame(self.BoxInfoCards, text="Nb Card on Table:", padx=2, pady=2)
        self.BoxNbCardTable.pack()
        self.nbCardTable = tk.StringVar()
        self.nbCardTable.set("")
        self.LabelNbCardTable = tk.Entry(self.BoxNbCardTable,textvariable = self.nbCardTable,width=10,state="disabled")
        self.LabelNbCardTable.pack()
        
        self.BoxInfoCardsTable = tk.LabelFrame(self.BoxInfoCards, text="", relief=tk.FLAT)
        self.BoxInfoCardsTable.pack()
        for row in range(self.nbCardsTable+1):
            tabTmp = []
            for col in range(self.nbTitleInfoGame):
                if row == 0:
                    vect = self.vectTitleInfoGame
                else:
                    vect = [" "," "]
                labelTmp = tk.Label(self.BoxInfoCardsTable, text=vect[col], borderwidth=2, relief=tk.GROOVE,width=10)
                tabTmp.append(labelTmp)
                labelTmp.grid(row=row, column=col)
            self.tabInfoGame.append(tabTmp)
                    

    def cbSaveScreenshot(self):
        screenshot = np.array(pyautogui.screenshot())
        screenshot = np.flip(screenshot,2)
        fileName = getDateAsString()
        saveArrayToPng("log/img/m"+fileName+".png",screenshot)
        
        
    def cbChangeImgSource(self,*args):
        if self.imgSource.get() == "File":
            self.entreeImgSource.config(state=tk.NORMAL)
        elif self.imgSource.get() == "Screen":
            self.entreeImgSource.config(state=tk.DISABLED)
        
        
    def updateTabInfoPlayer(self,listPlayer):
        # self.tab[1][1].config(text="new")
        for i in range(self.nbPerson):
            if i < len(listPlayer):
                if listPlayer[i].role == "dealer":
                    isdealer = "x"
                else:
                    isdealer = " "
                vect = [listPlayer[i].name,listPlayer[i].nbCoinHand,listPlayer[i].nbCoinTable,isdealer,listPlayer[i].lastAction]
            else:
                vect = [" "," "," "," "," "]
            for j in range(len(vect)):
                self.tab[i+1][j].config(text=vect[j])
                
    def updateTabInfoGame(self,listCardTable):
        for i in range(self.nbCardsTable):
            if i < len(listCardTable) and type(listCardTable[i]).__name__ != "list":
                vect = [listCardTable[i].val,listCardTable[i].fam]
            else:
                vect = [" "," "]
            for j in range(len(vect)):
                self.tabInfoGame[i+1][j].config(text=vect[j])
                
    def updateTabMyHand(self,listCardMyHand):
        for i in range(self.nbCardsMyHand):
            if i < len(listCardMyHand):
                vect = [listCardMyHand[i].val,listCardMyHand[i].fam]
            else:
                vect = [" "," "]
            for j in range(len(vect)):
                self.tabInfoMyHand[i+1][j].config(text=vect[j])
                
    def updatePot(self,valPot,valPotTotal):
        self.valPot.set(valPot)
        self.valPotTotal.set(valPotTotal)
        
                
    def cbStartBotBackGround(self):
        t = threading.Thread(target=self.cbStartBot)
        t.start()
        
    def getScreenShot(self):
        if self.imgSource.get() == "Screen":
            screenshot = np.array(pyautogui.screenshot())
            screenshot = np.flip(screenshot,2)

        elif self.imgSource.get() == "File":
            screenshot = cv2.imread(self.fileNameImgSource.get())
        return screenshot
    
    def cbStartBot(self):
        if self.toggleLoop.get() == True:
            self.buttonState = not self.buttonState
            if self.buttonState == False:
                self.boutonStartBot.config(text="Start")
            else:
                self.boutonStartBot.config(text="Stop")

        while True:                
            screenshot = self.getScreenShot()

            self.initData()
            self.updateData(screenshot)
            
            self.parent.update_idletasks()
            
            self.toggleActivity.set(not self.toggleActivity.get())
            
            if self.toggleLoop.get() == False or self.buttonState == False:
                break
        
        
    def initData(self):
        pass
        
    def updateData(self,screenshot):
        self.window,self.MPx,self.MPy = imgAn.findWindow(screenshot)
        if type(self.window).__name__ != "list":
            flagMyTurn = imgAn.isMyTurn(self.window)
            self.boolIsMyTurn.set(flagMyTurn)
            if  self.boolIsMyTurn.get() == True:
                #repeat the screenshot after a break, to avoid blur images
                sleep(0.8)
                screenshot = self.getScreenShot()
                self.window,self.MPx,self.MPy = imgAn.findWindow(screenshot)
                
                self.boolTableDetected.set(True)
                # imgAn.showImg(self.window)
                cardsTable = imgAn.detectCards(self.window,verbose=False)
                self.stateName = imgAn.getStateGame(len(cardsTable))
                windowDetectPlayers,listPlayer = imgAn.detectPlayers(self.window,self.stateName)
                nbPlayer = len(listPlayer)

                myCards = imgAn.readMyCards(self.window,listPlayer,verbose=False)

                valPot = imgAn.getPot(self.window,potTotal=False)
                valPotTotal = imgAn.getPot(self.window,potTotal=True)

                # for i in range(len(cardsTable))
                self.nbPlayer.set(nbPlayer)
                self.updateTabInfoPlayer(listPlayer)
                self.nbCardTable.set(len(cardsTable))
                self.updateTabInfoGame(cardsTable)
                self.updatePot(valPot,valPotTotal)
                self.updateTabMyHand(myCards)
            
            
                
                if self.boolEnableLogScreenShot.get() == True:
                    fileName = getDateAsString()
                    saveArrayToPng("log/img/a"+fileName+".png",screenshot)
            
                if len(myCards) == 2:
                    vectCardsJ1 = [myCards[0].val+myCards[0].fam,myCards[1].val+myCards[1].fam]
                else:
                    vectCardsJ1 = []
                vectCardsJ2 = []
                    
                if int(self.nbCardTable.get()) >= 1:
                    for i in range(int(self.nbCardTable.get())):
                        if type(cardsTable[i]).__name__ != "list":
                            tmp = cardsTable[i].val+cardsTable[i].fam
                            vectCardsJ1.append(tmp)
                            vectCardsJ2.append(tmp)
                        else:
                            print("Warning: one of the card on the table has been mis detected")
    
                # cardsJ1 = prbAn.genrateHandFromStrList(vectCardsJ1)
                # cardsJ2 = prbAn.genrateHandFromStrList(vectCardsJ2)
            
                # decision,chance,limitNbPlayer = prbAn.decision(cardsJ1,cardsJ2,nbPlayer,int(self.varSpinBoxNbRunSim.get()),verbose=False)
                
                cardsJ1 = prbAn.genrateHandFromStrList(vectCardsJ1)
                cardsOtherP = prbAn.genrateHandFromStrList(vectCardsJ2)
                cardsAllP = [cardsJ1]
                for i in range(nbPlayer-1):
                    cardsAllP.append(cardsOtherP)
                
            
                decision,chance,limitNbPlayer = prbAn.decision(cardsAllP,int(self.varSpinBoxNbRunSim.get()),verbose=False)
                if valPotTotal == 0:
                    valPotTotalTmp = valPot
                else:
                    valPotTotalTmp = valPotTotal
                
                betMax = chance*valPotTotalTmp/(1.000001-chance)
                self.valBetMax.set(betMax)
                self.valChanceOfWin.set(chance)
                self.valAction.set(decision)
                self.valLimitNbPlayer.set(limitNbPlayer)
                
                if self.boolEnableBotPlay.get() == True:
                    possibleActions,locActions = imgAn.detectPossibleActions(self.window)
                    
                    if self.stateName == "begining" and chance > limitNbPlayer+0.1:
                        decision = decision+["follow"]


                    flagNoActionPossible = True
                    for i in range(len(decision)):
                        if decision[i] in possibleActions:
                            finalDecision = decision[i]
                            index = possibleActions.index(finalDecision)
                            clickY = locActions[index][0]
                            clickX = locActions[index][1]
                            flagNoActionPossible = False
                            break
                        
                    if flagNoActionPossible == False:
                        self.valAction.set(finalDecision)
                    else:
                        print("Warning: No matching action possible. Possible action: ",possibleActions," Decisions: ",decision)
                        
                    pyautogui.click(self.MPx+clickX, self.MPy+clickY)
                    pyautogui.moveTo(self.MPx+clickX, self.MPy+clickY+20)
            else:
                self.boolTableDetected.set(False)
                # print("Error: no poker window detected")
        
        
        

if __name__ == "__main__":
    root = tk.Tk()
    AppPokerBot(root)
    root.mainloop()