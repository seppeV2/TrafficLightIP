import pathlib
from PIL import Image, ImageDraw, ImageFont
import numpy as np
from greenTimes import get_link_delay
#install opencv-python for this (via pip)
import cv2
import os

def text_to_image(textString, size = 'summary'):
    img = Image.new('RGB', (550, 400), (255, 255, 255)) if size == 'summary' else Image.new('RGB', (1050, 450), (255, 255, 255))
    d = ImageDraw.Draw(img)
    font = ImageFont.truetype(str(pathlib.Path(__file__).parent)+"/data/Gidole-Regular.ttf", size=17)
    d.text((20, 20), textString, fill=(0, 0, 0), font = font)
    file_name = 'text_{}.png'.format(size)
    path = str(pathlib.Path(__file__).parent)+'/summaryFiles/rawFigures/'
    os.makedirs(path, exist_ok=True)
    img.save(path+file_name)
    return file_name

def create_summary(listOfPlots, string, property_string, method, policy, network_type, demand, greenDistribution):
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
    path = str(pathlib.Path(__file__).parent)+f'/summaryFiles/{network_type}/{method}_{policy}/{demand}/'
    os.makedirs(path, exist_ok=True)
    cv2.imwrite(path+'summary_{}.png'.format(greenDistribution), vstack)



def demand_summary(O_or_D, OD_flow, signalized_nodes):
    string = '\n\nDemands\n'
    for (o,d,flow) in OD_flow:
        string+='- {} flow from: Origin_{} ->  Destination_{}\n'.format(flow, o, d)
    string += '\n\nSignalized nodes\n'
    for node_id in signalized_nodes:
        string += '- node {}\n'.format(node_id)
    string += '\n\nLegend:\n- black numbers = node_ids\n- red numbers = signalized node_ids\n- blue numbers = link_ids\n- green numbers = OD_ids'

    return string

def result_summary(result,greens, capacities, non_connectors,safety_loops, first_greens, ff_tts, method, methodCost):
    step = 0
    string = '\nSummary of the results:\n\n'
    string0 = '- The link first green times = '
    string1 = '- The link flows = '
    string2 = '- The link costs = '
    string3 = '- The link green times = '
    string4 = '- The link capacities = '

    string4b = '- The link dos = ' if method == 'equisaturation' else '- The link pressure = '
    string5bis = ' (converged)' if safety_loops != 100 else ' (non-converged)'
    string5 = f'- The amount of iterations needed = {safety_loops}' + string5bis

    veh_hours = 0
    for idx, (flow, cost, cap) in enumerate(zip(result.flows, result.link_costs, capacities,)):
        if idx in non_connectors:
            string0 += '({}, {}), '.format(idx,round(first_greens[idx],2))
            string1 += '({}, {}), '.format(idx,round(flow,2)) 
            string2 += '({}, {}), '.format(idx,round(cost,2))        
            string3 += '({}, {}), '.format(idx,round(greens[idx],2))
            string4 += '({}, {}), '.format(idx,round(cap,2))
            veh_hours += flow*cost
            if method == 'equisaturation': string4b += '({}, {}), '.format(idx,round((result.flows[idx]/(greens[idx]*capacities[idx])),4))
            else: string4b += '({}, {}), '.format(idx,round(cap*get_link_delay(flow,cap,ff_tts[idx],greens[idx], methodCost),4))
            
            step+=1

            if (step)%10 == 0:
                string0 += '\n                                           '
                string1 += '\n                          '
                string2 += '\n                          '
                string3 += '\n                                    '
                string4 += '\n                                 '
                string4b += '\n                                 '
    string0 += '\n\n'
    string1 += '\n\n'
    string2 += '\n\n'
    string3 += '\n\n'
    string4 += '\n\n'
    string4b += '\n\n'
    string5 += '\n\n'
    
    string6 = f'- The network vehicle hours = {round(veh_hours,3)}'

    return string+string0+string1+string2+string3+string4+string4b+string5+string6
