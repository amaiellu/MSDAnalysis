'''
Created on Sep 4, 2016

@author: amschaef
'''
import pandas as pd
import os
def checkdups(myfile):
    data=pd.read_excel(myfile,sheetname='XY Final',parse_cols='A:B',header=None,names=['particle','frame'])
    data['is_duplicated']=data.duplicated()
    dups=data[data['is_duplicated']==True]
    return data

files=os.listdir('C:\\Users\\amschaef\\Documents\\GrantData\\ManualTrack\\Reformatted_Data_Files\\Linked Files\\Compiled XY Data')

for file in files:

    checkdups(os.path.join('C:\\Users\\amschaef\\Documents\\GrantData\\ManualTrack\\Reformatted_Data_Files\\Linked Files\\Compiled XY Data',file))