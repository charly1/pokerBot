# -*- coding: utf-8 -*-
"""
Created on Thu Feb  6 15:52:52 2020

@author: Charly
"""

import tkinter as tk
from PIL import ImageTk
from PIL import Image


root = tk.Tk()

path = "img/test.png"
img = ImageTk.PhotoImage(Image.open(path))
panel = tk.Label(root, image=img)
panel.pack(side="bottom", fill="both", expand="yes")

def callback(e):
    img2 = ImageTk.PhotoImage(Image.open(path2))
    panel.configure(image=img2)
    panel.image = img2

root.bind("<Return>", callback)
root.mainloop()