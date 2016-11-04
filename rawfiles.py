'''
Created on Aug 5, 2016

@author: amschaef
'''
import os, shutil
# how to handle if there is more than one file? i.e. in case that tmp is still there-- check for if file matches movie name exactly?
def attempt():
    
    for root, dirs, files in os.walk("."):
        if not dirs:
            for file in files:
                folder=os.path.basename(root)
                
                if file.endswith(".xlsx") and not file.endswith('_tmp.csv'):
                    #os.rename(os.path.join(root,file),os.path.join(root,folder+'.csv'))
                    shutil.move(os.path.join(root,file),'C:\\Users\\amschaef\\Documents\\Lai Lab\\Ebola in AM study\\Reformatted_Data_Files\\Files For Check Tracking\\Links')
                    


def groupframes(data):
    frames=data['frame'].values
    
    count=0
    particles=[]
    for i in range(1,len(frames)):
        if frames[i]!=frames[i-1]+1:
            particles=np.append(particles,data.iloc[i-1].particle)
            count=count+1
    print (particles)
    return count+1
import pandas as pd
import numpy as np
data=pd.read_excel('C:\\Users\\amschaef\\Downloads\\no linking\\Individual Movie XY Data\\Compiled Movies\\F21 140620 pH.xlsx',index_col=None,header=None,names=['particle','frame','x','y'],sheetname='Sheet1')
import AnalysisPackage as ap
blanks=ap.insert_blanks(data)
writer = pd.ExcelWriter('C:\\Users\\amschaef\\Downloads\\no linking\\Individual Movie XY Data\\Compiled Movies\\ F21 140620 pH blanks.xlsx', engine='xlsxwriter')   
blanks.to_excel(writer)
writer.save()
groupframes(blanks)
x=0
#os.chdir('C:\\Users\\amschaef\\Documents\\Lai Lab\\Ebola in AM study\\Reformatted_Data_Files\\Files For Check Tracking\\Links')
#attempt()