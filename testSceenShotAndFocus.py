# -*- coding: utf-8 -*-
"""
Created on Mon Feb 10 08:27:40 2020

@author: Charly
"""

from PIL import ImageGrab
import win32gui, win32com.client
import imageAnalysis as imgAn
import numpy as np

def getNbWindowGameOpen():
    toplist, winlist = [], []
    def enum_cb(hwnd, results):
        winlist.append((hwnd, win32gui.GetWindowText(hwnd)))
    win32gui.EnumWindows(enum_cb, toplist)
    
    pokerWin = [(hwnd, title) for hwnd, title in winlist if 'holdem' in title.lower()]
    return pokerWin

def takeScreenShotOfSpecificWin(idWin):
    shell = win32com.client.Dispatch("WScript.Shell")
    shell.SendKeys('%')
    win32gui.SetForegroundWindow(idWin)
    bbox = win32gui.GetWindowRect(idWin)
    img = np.array(ImageGrab.grab(bbox))
    img = np.flip(img,2)
    return img


if __name__ == "__main__":
    
    listWin = getNbWindowGameOpen()
    for i in range(len(listWin)):
        takeScreenShotOfSpecificWin(listWin[i][0])