# -*- coding: utf-8 -*-
"""
Created on Sun Dec 29 17:36:23 2019

@author: Charly
"""

import tkinter as tk
import imageAnalysis as imgAn
import cv2
import numpy as np
import pyautogui
import threading
from PIL import Image
import pyautogui


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
        
        self.BoxCmd = tk.LabelFrame(self.parent, text="Commands", padx=5, pady=5)
        self.BoxCmd.pack()   
        
        self.BoxSelectImgSource = tk.LabelFrame(self.BoxCmd, text="Image from", padx=3, pady=3)
        self.BoxSelectImgSource.pack()
        self.imgSource = tk.StringVar(self.BoxSelectImgSource)
        self.imgSource.set("File") # default value
        self.imgSource.trace('w',self.cbChangeImgSource)
        self.optionMenuReconstr = tk.OptionMenu(self.BoxSelectImgSource, self.imgSource, *["File","Screen"])
        self.optionMenuReconstr.pack(side=tk.LEFT)
        self.fileNameImgSource = tk.StringVar() 
        self.fileNameImgSource.set("img/test.png")
        self.entreeImgSource = tk.Entry(self.BoxSelectImgSource, textvariable=self.fileNameImgSource, width=20)
        self.entreeImgSource.pack(side=tk.RIGHT)
        
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
        self.toggleLoop.set(True)
        self.CBtoggleLoop = tk.Checkbutton(self.BoxRun, text="Loop", variable=self.toggleLoop)
        self.CBtoggleLoop.pack(side=tk.RIGHT)
        
        self.boolEnableBotPlay = tk.IntVar()
        self.boolEnableBotPlay.set(False)
        self.CBboolEnableBotPlay = tk.Checkbutton(self.BoxCmd, text="Enable Bot Play", variable=self.boolEnableBotPlay)
        self.CBboolEnableBotPlay.pack()


        self.BoxNbPlayer = tk.LabelFrame(self.parent, text="Nb Player:", padx=5, pady=5)
        self.BoxNbPlayer.pack()
        self.nbPlayer = tk.StringVar()
        self.nbPlayer.set("")
        self.LabelNbPlayer = tk.Label(self.BoxNbPlayer,textvariable = self.nbPlayer)
        self.LabelNbPlayer.pack()

        self.BoxNbPlayer = tk.LabelFrame(self.parent, text="Info Players:", padx=5, pady=5)
        self.BoxNbPlayer.pack()
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
                labelTmp = tk.Label(self.BoxNbPlayer, text=vect[col], borderwidth=2, relief=tk.GROOVE,width=10)
                tabTmp.append(labelTmp)
                labelTmp.grid(row=row, column=col)
            self.tab.append(tabTmp)
            
        self.BoxMyCard = tk.LabelFrame(self.parent, text="My Cards", padx=5, pady=5)
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
            
        # self.card1 = tk.StringVar()
        # self.card1.set(" ")
        # self.LabelCard1 = tk.Label(self.BoxMyCard,textvariable = self.card1,relief=tk.GROOVE)
        # self.LabelCard1.pack(side=tk.LEFT)
        # self.card2 = tk.StringVar()
        # self.card2.set(" ")
        # self.LabelCard2 = tk.Label(self.BoxMyCard,textvariable = self.card2,relief=tk.GROOVE)
        # self.LabelCard2.pack(side=tk.RIGHT)
        
        self.BoxNbCardTable = tk.LabelFrame(self.parent, text="Nb Card on Table:", padx=5, pady=5)
        self.BoxNbCardTable.pack()
        self.nbCardTable = tk.StringVar()
        self.nbCardTable.set("")
        self.LabelNbCardTable = tk.Label(self.BoxNbCardTable,textvariable = self.nbCardTable)
        self.LabelNbCardTable.pack()
        
        self.BoxInfoGame = tk.LabelFrame(self.parent, text="Info Game:", padx=5, pady=5)
        self.BoxInfoGame.pack()
        self.nbCardsTable = 5
        self.tabInfoGame = []
        for row in range(self.nbCardsTable+1):
            tabTmp = []
            for col in range(self.nbTitleInfoGame):
                if row == 0:
                    vect = self.vectTitleInfoGame
                else:
                    vect = [" "," "]
                labelTmp = tk.Label(self.BoxInfoGame, text=vect[col], borderwidth=2, relief=tk.GROOVE,width=10)
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
            if i < len(listCardTable):
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
        if not self.window == []:
            # imgAn.showImg(self.window)
            windowDetectPlayers,listPlayer = imgAn.detectPlayers(self.window)
            nbPlayer = len(listPlayer)
            idxDealer = imgAn.getDealerIndex(self.window,listPlayer)
            imgAn.setNewDealer(listPlayer,idxDealer)
            myCards = imgAn.readMyCards(self.window,listPlayer)
            cardsTable = imgAn.detectCards(self.window)
            flagMyTurn,xButton,yButton = imgAn.isMyTurn(self.window)
            self.nbPlayer.set(nbPlayer)
            self.updateTabInfoPlayer(listPlayer)
            self.nbCardTable.set(len(cardsTable))
            self.updateTabInfoGame(cardsTable)
            self.boolIsMyTurn.set(flagMyTurn)
            self.updateTabMyHand(myCards)
            
            if self.boolEnableBotPlay.get() == True and flagMyTurn == True:
                pyautogui.click(self.MPx+xButton, self.MPy+yButton)
        else:
            print("Error: no poker window detected")
        
        
            
            

if __name__ == "__main__":
    root = tk.Tk()
    AppPokerBot(root)
    root.mainloop()