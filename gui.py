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

def saveArrayToPng(filename,array):
    im = Image.fromarray(np.flip(array,axis=2))
    im.save(filename)

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
        
        self.BoxSaveScreenShot = tk.LabelFrame(self.BoxCmd, text="Screenshot", padx=3, pady=3)
        self.BoxSaveScreenShot.pack(fill="both", expand="yes")
        self.boutonSaveScreenShot=tk.Button(self.BoxSaveScreenShot, text="Save", command=self.cbSaveScreenshot)
        self.boutonSaveScreenShot.pack(padx=5, pady=5,side=tk.LEFT)
        self.fileNameScreenshot = tk.StringVar() 
        self.fileNameScreenshot.set("img/screenshot.png")
        self.entreeImgScreenshot = tk.Entry(self.BoxSaveScreenShot, textvariable=self.fileNameScreenshot, width=20)
        self.entreeImgScreenshot.pack(side=tk.RIGHT)
        
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
        
        self.boolEnableLogScreenShot = tk.IntVar()
        self.boolEnableLogScreenShot.set(True)
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
        self.LabelNbPlayer = tk.Label(self.BoxNbPlayer,textvariable = self.nbPlayer)
        self.LabelNbPlayer.pack()
        
        self.BoxAroundTabPlayers = tk.LabelFrame(self.BoxInfoPlayer, text="", relief=tk.FLAT)
        self.BoxAroundTabPlayers.pack()
        self.vectTitle = ["Name","Coin Hand","Coin Table","Dealer"]
        self.nbPerson = 10
        self.nbTitleInfoPlayer = len(self.vectTitle)
        self.tab = []
        for row in range(self.nbPerson+1):
            tabTmp = []
            for col in range(self.nbTitleInfoPlayer):
                if row == 0:
                    vect = self.vectTitle
                else:
                    vect = [" "," "," "," "]
                labelTmp = tk.Label(self.BoxAroundTabPlayers, text=vect[col], borderwidth=2, relief=tk.GROOVE,width=10)
                tabTmp.append(labelTmp)
                labelTmp.grid(row=row, column=col)
            self.tab.append(tabTmp)
            
        self.BoxInfoCards = tk.LabelFrame(self.BoxInfos, text="Info Cards:", padx=2, pady=2)
        self.BoxInfoCards.pack(side=tk.LEFT,fill=tk.BOTH)


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
        self.BoxNbCardTable.pack(fill=tk.BOTH)
        self.nbCardTable = tk.StringVar()
        self.nbCardTable.set("")
        self.LabelNbCardTable = tk.Label(self.BoxNbCardTable,textvariable = self.nbCardTable)
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
        im = Image.fromarray(np.flip(self.window,2))
        im.save(self.fileNameScreenshot.get())
        
        
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
                vect = [listPlayer[i].name,listPlayer[i].nbCoinHand,listPlayer[i].nbCoinTable,isdealer]
            else:
                vect = [" "," "," "," "]
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
                
    def cbStartBotBackGround(self):
        t = threading.Thread(target=self.cbStartBot)
        t.start()
    
    def cbStartBot(self):
        if self.toggleLoop.get() == True:
            self.buttonState = not self.buttonState
            if self.buttonState == False:
                self.boutonStartBot.config(text="Start")
            else:
                self.boutonStartBot.config(text="Stop")

        while True:
            if self.imgSource.get() == "Screen":
                screenshot = np.array(pyautogui.screenshot())
                screenshot = np.flip(screenshot,2)
    
            elif self.imgSource.get() == "File":
                screenshot = cv2.imread(self.fileNameImgSource.get())

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
                self.boolTableDetected.set(True)
                # imgAn.showImg(self.window)
                windowDetectPlayers,listPlayer = imgAn.detectPlayers(self.window)
                nbPlayer = len(listPlayer)
                idxDealer = imgAn.getDealerIndex(self.window,listPlayer)
                imgAn.setNewDealer(listPlayer,idxDealer)
                myCards = imgAn.readMyCards(self.window,listPlayer)
                cardsTable = imgAn.detectCards(self.window,verbose=False)
                if len(cardsTable) == 0:
                    self.stateName = "begining"
                elif len(cardsTable) == 3:
                    self.stateName = "flop"
                elif len(cardsTable) == 4:
                    self.stateName = "turn"
                elif len(cardsTable) == 5:
                    self.stateName = "river"
                # for i in range(len(cardsTable))
                self.nbPlayer.set(nbPlayer)
                self.updateTabInfoPlayer(listPlayer)
                self.nbCardTable.set(len(cardsTable))
                self.updateTabInfoGame(cardsTable)
                
                self.updateTabMyHand(myCards)
            
            
                
                if self.boolEnableLogScreenShot.get() == True:
                    fileName = datetime.datetime.now().strftime("%I%M%S_%m%d%Y")
                    saveArrayToPng("log/img/"+fileName+".png",screenshot)
            
                if len(myCards) == 2:
                    vectCardsJ1 = [myCards[0].val+myCards[0].fam,myCards[1].val+myCards[1].fam]
                else:
                    vectCardsJ1 = []
                vectCardsJ2 = []
                    
                if int(self.nbCardTable.get()) >= 1:
                    for i in range(int(self.nbCardTable.get())):
                        tmp = cardsTable[i].val+cardsTable[i].fam
                        vectCardsJ1.append(tmp)
                        vectCardsJ2.append(tmp)
    
                cardsJ1 = prbAn.genrateHandFromStrList(vectCardsJ1)
                cardsJ2 = prbAn.genrateHandFromStrList(vectCardsJ2)
            
                decision,chance,limitNbPlayer = prbAn.decision(cardsJ1,cardsJ2,nbPlayer,int(self.varSpinBoxNbRunSim.get()),verbose=True)
                self.valChanceOfWin.set(chance)
                self.valAction.set(decision)
                self.valLimitNbPlayer.set(limitNbPlayer)
                
                if self.boolEnableBotPlay.get() == True:
                    possibleActions,locActions = imgAn.detectPossibleActions(self.window)
                    print("possibleActions:",possibleActions,locActions)
                    if self.stateName == "begining":
                        self.valAction.set("follow")
                    
                    if self.valAction.get() == "quit":
                        if "parole" in possibleActions:
                            index = possibleActions.index("parole")
                        elif "passer" in possibleActions:
                            index = possibleActions.index("passer")
                        else:
                            print("Error: no action detected")
                            index = imgAn.OUT_OF_INDEX()
                        if index == imgAn.OUT_OF_INDEX():
                            clickX = 0
                            clickY = 0
                        else:
                            clickY = locActions[index][0]
                            clickX = locActions[index][1]

                    elif self.valAction.get() == "follow":
                        if "parole" in possibleActions:
                            index = possibleActions.index("parole")
                        elif "suivrve" in possibleActions:
                            index = possibleActions.index("suivrve")
                        else:
                            print("Error: no action detected",possibleActions)
                            index = imgAn.OUT_OF_INDEX()
                        if index == imgAn.OUT_OF_INDEX():
                            clickX = 0
                            clickY = 0
                        else:
                            clickY = locActions[index][0]
                            clickX = locActions[index][1]
                    pyautogui.click(self.MPx+clickX, self.MPy+clickY)
                    pyautogui.move(self.MPx, self.MPy)
            else:
                self.boolTableDetected.set(False)
                # print("Error: no poker window detected")
        
        
        

if __name__ == "__main__":
    root = tk.Tk()
    AppPokerBot(root)
    root.mainloop()