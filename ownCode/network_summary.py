import pathlib
from PIL import Image, ImageDraw, ImageFont
import numpy as np
from html2image import Html2Image
import os
#install opencv-python for this (via pip)
import cv2

def text_to_image(textString):
    img = Image.new('RGB', (500, 400), (255, 255, 255))
    d = ImageDraw.Draw(img)
    font = ImageFont.truetype(str(pathlib.Path(__file__).parent)+"/data/Gidole-Regular.ttf", size=17)
    d.text((20, 20), textString, fill=(0, 0, 0), font = font)
    file_name = 'text.png'
    img.save(str(pathlib.Path(__file__).parent)+'/summaryFiles/rawFigures/'+file_name)
    return file_name

def create_summary(listOfPlots, string, method, policy, demand, greenPolicy):
    text_image = text_to_image(string)
    listOfPlots.insert(1,text_image)
    vstack = []
    hstack = []
    for i in range(len(listOfPlots)):
        figure = cv2.imread(str(pathlib.Path(__file__).parent)+'/summaryFiles/rawFigures/'+listOfPlots[i])
        figure = cv2.resize(figure, (500,400))
        hstack.append(figure)
        if (i%2 == 1 and i>0):
            vstack.append(np.hstack(hstack))
            hstack = []
        
        if i == len(listOfPlots)-1 and i%2 == 0:
            hstack.append(np.full((400,500,3),255, np.uint8))
            vstack.append(np.hstack(hstack))      
    vstack = np.vstack(vstack)
    path = str(pathlib.Path(__file__).parent)+'/summaryFiles/D={}/'.format(demand)
    os.makedirs(path, exist_ok=True)
    cv2.imwrite(path+'summary_{}_{}_{}.png'.format(method, policy, greenPolicy), vstack)



