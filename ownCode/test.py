from numpy import *
import os
import pathlib


print(str(pathlib.Path(__file__).parent)+'/data/ODmatrix.csv')
my_data = genfromtxt(str(pathlib.Path(__file__).parent)+'/data/ODmatrix.csv', delimiter=',')
print(my_data)