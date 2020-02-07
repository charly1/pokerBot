# -*- coding: utf-8 -*-
"""
Created on Thu Feb  6 15:40:31 2020

@author: Charly
"""

import tkinter as tk
from PIL import ImageTk
from PIL import Image
import imageAnalysis as imgAn
import numpy as np
import cv2
import copy


# root = tk.Tk()

# img = ImageTk.PhotoImage(Image.open(path))
# panel = tk.Label(root, image=img)
# panel.pack(side="bottom", fill="both", expand="yes")



# root.bind("<Return>", callback)
# root.mainloop()

def saveArrayToPng(filename,array):
    im = Image.fromarray(np.flip(array,axis=2))
    im.save(filename)


class AppTestFilter(tk.Frame):
    def __init__(self, parent, pathFile, *args, **kwargs):
        self.parent = parent
        self.path = pathFile
              
        self.valHinit = tk.DoubleVar()
        self.valHinit.set(0)
        self.valHinit.trace("w",self.cbSliders)
        self.scaleHinit = tk.Scale(self.parent, variable=self.valHinit,orient='horizontal',from_=0, to=255,length=255,label='H init')
        self.scaleHinit.pack()
        
        self.valSinit = tk.DoubleVar()
        self.valSinit.set(0)
        self.valSinit.trace("w",self.cbSliders)
        self.scaleSinit = tk.Scale(self.parent, variable=self.valSinit,orient='horizontal',from_=0, to=255,length=255,label='S init')
        self.scaleSinit.pack()
        
        self.valLinit = tk.DoubleVar()
        self.valLinit.set(0)
        self.valLinit.trace("w",self.cbSliders)
        self.scaleLinit = tk.Scale(self.parent, variable=self.valLinit,orient='horizontal',from_=0, to=255,length=255,label='L init')
        self.scaleLinit.pack()
        
        self.valHfinal = tk.DoubleVar()
        self.valHfinal.set(40)
        self.valHfinal.trace("w",self.cbSliders)
        self.scaleHfinal = tk.Scale(self.parent, variable=self.valHfinal,orient='horizontal',from_=0, to=255,length=255,label='H final')
        self.scaleHfinal.pack()
        
        self.valSfinal = tk.DoubleVar()
        self.valSfinal.set(40)
        self.valSfinal.trace("w",self.cbSliders)
        self.scaleSfinal = tk.Scale(self.parent, variable=self.valSfinal,orient='horizontal',from_=0, to=255,length=255,label='S final')
        self.scaleSfinal.pack()
        
        self.valLfinal = tk.DoubleVar()
        self.valLfinal.set(40)
        self.valLfinal.trace("w",self.cbSliders)
        self.scaleLfinal = tk.Scale(self.parent, variable=self.valLfinal,orient='horizontal',from_=0, to=255,length=255,label='L final')
        self.scaleLfinal.pack()
        
        self.boutonPrintVal=tk.Button(self.parent, text="Print HSV values", command=self.cbPrintHslVal)
        self.boutonPrintVal.pack()
        

        
        img = ImageTk.PhotoImage(Image.open(self.path))
        self.panel = tk.Label(self.parent, image=img)
        self.panel.pack(side="bottom", fill="both", expand="yes")
        
        self.cbImg()

    def cbImg(self):
        if True:
            img = Image.open(self.path)
            img2 = np.array(img)
            img2 = np.flip(img,2)
        else:
            img2 = cv2.imread(self.path)
        
        self.imgNotFiltered = copy.copy(img2)
        
        self.l1 = [int(self.valHinit.get()),int(self.valSinit.get()),int(self.valLinit.get())]
        self.l2 = [int(self.valHfinal.get()),int(self.valSfinal.get()),int(self.valLfinal.get())]
        
        img2 = imgAn.filterColorV2(img2,self.l1,self.l2,inverse=True)
        
        self.imgFiltered = copy.copy(img2)
        
        # img2 = imgAn.filterColorV2(img2,[65,229,0],[117,255,255],inverse=True,flip=True)
        
        img2 = np.flip(img2,2)
        img2 = Image.fromarray(img2)
        img2 = ImageTk.PhotoImage(img2)
        self.panel.configure(image=img2)
        self.panel.image = img2
        
        
    def cbSliders(self,*arg):
        self.cbImg()
        
    def cbPrintHslVal(self):
        print(self.l1,",",self.l2)
        
        
        
if __name__ == "__main__":
    path = "log/img/035938_02052020.png"
    root = tk.Tk()
    AppTestFilter(root,path)
    root.mainloop()