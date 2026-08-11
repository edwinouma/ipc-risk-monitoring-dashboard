import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os

os.chdir(r'C:\WORK\IPC-HQ\RAAP - RISK ANALYSIS APPROACH\AFGHANISTAN\CLIMATOLOGICAL\pythonProject\data')

morbidity_ke = pd.read_excel('morbidity_kenya.xlsx')
morbidity_ke.head(5)

morbidity_ke = morbidity_ke[['country', 'county', 'sub_county', 'Malaria', 'Diarrhoea']]