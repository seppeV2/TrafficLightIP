import pathlib
from PIL import Image, ImageDraw, ImageFont
import numpy as np
from html2image import Html2Image
#install opencv-python for this (via pip)
import cv2

def text_to_image(textString, size = 'summary'):
    img = Image.new('RGB', (550, 400), (255, 255, 255)) if size == 'summary' else Image.new('RGB', (1050, 350), (255, 255, 255))
    d = ImageDraw.Draw(img)
    font = ImageFont.truetype(str(pathlib.Path(__file__).parent)+"/data/Gidole-Regular.ttf", size=17)
    d.text((20, 20), textString, fill=(0, 0, 0), font = font)
    file_name = 'text_{}.png'.format(size)
    img.save(str(pathlib.Path(__file__).parent)+'/summaryFiles/rawFigures/'+file_name)
    return file_name

def create_summary(listOfPlots, string, property_string, method, policy, network_type, demand):
    text_image1 = text_to_image(string)
    listOfPlots.insert(1,text_image1)
    text_image2 = text_to_image(property_string, 'result')
    listOfPlots.insert(2,text_image2)
    vstack = []
    hstack = []

    figure1 = cv2.imread(str(pathlib.Path(__file__).parent)+'/summaryFiles/rawFigures/'+listOfPlots[0])
    figure1 = cv2.resize(figure1, (500,400))
    figure2 = cv2.imread(str(pathlib.Path(__file__).parent)+'/summaryFiles/rawFigures/'+listOfPlots[1])
    figure3 = cv2.imread(str(pathlib.Path(__file__).parent)+'/summaryFiles/rawFigures/'+listOfPlots[2])

    hstack.append(figure1)
    hstack.append(figure2)
    vstack.append(np.hstack(hstack))
    vstack.append(figure3)

    vstack = np.vstack(vstack)

    cv2.imwrite(str(pathlib.Path(__file__).parent)+'/summaryFiles/summary_{}_{}_{}_D={}.png'.format(method, policy, network_type, demand), vstack)



def demand_summary(O_or_D, OD_flow, signalized_nodes):
    string = '\n\nDemands\n'
    for (o,d,flow) in OD_flow:
        string+='- {} flow from: Origin_{} ->  Destination_{}\n'.format(flow, o, d)
    string += '\n\nSignalized nodes\n'
    for node_id in signalized_nodes:
        string += '- node {}\n'.format(node_id)
    string += '\n\nLegend:\n- black numbers = node_ids\n- red numbers = signalized node_ids\n- blue numbers = link_ids\n- green numbers = OD_ids'

    return string

def result_summary(result,greens, capacities, non_connectors):
    step = 0
    string = '\nSummary of the results:\n\n'
    string1 = '- The link flows = '
    string2 = '- The link costs = '
    string3 = '- The link green times = '
    string4 = '- The link capacities = '
    for idx, (flow, cost, green, cap) in enumerate(zip(result.flows, result.link_costs, greens.values(), capacities)):
        if idx in non_connectors:
            string1 += '({}, {}), '.format(idx,round(flow,2)) 
            string2 += '({}, {}), '.format(idx,round(cost,2))        
            string3 += '({}, {}), '.format(idx,round(green,2))
            string4 += '({}, {}), '.format(idx,round(cap,2))
            step+=1

            if (step)%10 == 0:
                string1 += '\n                          '
                string2 += '\n                          '
                string3 += '\n                                    '
                string4 += '\n                                 '
    string1 += '\n\n'
    string2 += '\n\n'
    string3 += '\n\n'
    string4 += '\n\n'
    return string+string1+string2+string3+string4
