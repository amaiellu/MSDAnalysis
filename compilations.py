'''
Created on Aug 8, 2016

@author: amschaef
'''

import os
import pandas as pd
from numpy import isnan
import xlsxwriter
import numpy as np
import math
import shutil

def compile_movies(mydir):
    
    compilepath=os.path.join(mydir,'Compiled Movies')
    for dirpaths, dirnames, filenames in os.walk(mydir):
        if not dirnames:
            XY_all=pd.DataFrame(columns=['particle','frame','x','y'])
            for file in filenames:
                if file.endswith('.xlsx'):
                    this_movie=pd.read_excel(os.path.join(dirpaths,file),names=['particle','frame','x','y'])
                    max_particle=XY_all['particle'].max()
                    if ~isnan(max_particle):
                        empty=np.empty(this_movie.shape[0])
                        empty.fill(max_particle+1)
                        const=pd.Series(empty)
                        this_movie['particle']=np.add(this_movie['particle'],(const))
                            
                    XY_all=pd.concat([XY_all, this_movie],ignore_index=True)
            if filenames:
                fileparts=file.split('_')
                fileparts=fileparts[0:len(fileparts)-1]
                filename= '_'.join(fileparts)+'.xlsx' 
                writer = pd.ExcelWriter(os.path.join(mydir,compilepath,os.path.basename(dirpaths)+'.xlsx'), engine='xlsxwriter')
                if os.path.isdir(compilepath)==False:
                    os.mkdir(compilepath)       
                            
                XY_all.to_excel(writer,index=False)
                writer.save()                
    return
def fixfiles(mydir):
    import shutil
    for dirpaths, dirnames, filenames in os.walk(mydir):
        for file in filenames:
            
               
            basename=file.split('.')[0]
            basename=basename[0: len(basename)-10]
                    
            if os.path.isdir(os.path.join(dirpaths,basename))==False:
                    os.mkdir(os.path.join(dirpaths,basename))
            
            shutil.move(os.path.join(dirpaths,file),'\\\\?\\'+os.path.abspath(os.path.join(dirpaths,basename)))
            
    return

def tracelink(mydir,conversion,cutoff):
    if os.path.isdir(os.path.join(mydir,'Linked Files'))==False:
        os.mkdir(os.path.join(mydir,'Linked Files'))
    files=os.listdir(mydir)
    for file in files:
        data=pd.read_excel(os.path.join(mydir,file),header=None,names=['particle','frame','x','y'],sheetname='Sheet3')
        exits=data.groupby('particle', as_index=False).apply(lambda p: p.tail(1))
        entries=data.groupby('particle').apply(lambda p: p.iloc[0])
        for i in range(0,exits.shape[0]):
            frame=exits.iloc[i].frame
            comp_entries=entries.groupby('particle').filter(lambda p: p.frame>frame)
            comp_entries=comp_entries.groupby('particle').filter(lambda p: conversion**2*((p.x-exits.iloc[i].x)**2+(p.y-exits.iloc[i].y)**2)<cutoff)
            if (len(comp_entries)!=0):
                if (len(comp_entries)>1):
                    min=302
                    for j in range(0,len(comp_entries)):
                        if(comp_entries.iloc[j].frame-frame<min):
                           min=comp_entries.iloc[j].frame-frame
                           mindex=j
                
                    
                    comp_entries=comp_entries.iloc[mindex]
                droppart=math.floor(comp_entries.particle)
                entries=entries.drop(droppart)
                x=exits[exits['particle']==droppart].index.labels[0][0]
                exits.loc[x,'particle']=exits.iloc[i].particle
            #temp=np.empty(data[data['particle']==comp_entries['particle'].values[0]].shape[0])
            #temp=temp.fill(exits.iloc[i].particle)
                ind=data[data['particle']==droppart].index
                data.loc[ind,'particle']=exits.iloc[i].particle
                print(i)
        data.sort_values(['particle','frame'],inplace=True)
        writer=pd.ExcelWriter(os.path.join(mydir,'Linked Files',file), engine='xlsxwriter')
        data.to_excel(writer)   
        writer.save()
        shutil.move(os.path.join(mydir,file),'C:\\Users\\amschaef\\Documents\\Lai Lab\\Ebola in AM study\\Reformatted_Data_Files\\unaltered')
        
    return
    
def filesearch(dir):
        import shutil
        folders=list(os.listdir(dir));
        folders.remove('z')
        folders.remove('Compiled Movies')
        files=list(os.listdir(os.path.join(dir,'Compiled Movies')))
        files=[os.path.splitext(file)[0] for file in files]

        for folder in folders:
            if folder not in files:
                shutil.move(os.path.join(dir,folder),os.path.join(dir,'z'))
        
        return 
    
tracelink('C:\\Users\\amschaef\\Documents\\Lai Lab\\Ebola in AM study\\Reformatted_Data_Files',.156,5)
#fixfiles('C:\\Users\\amschaef\\Documents\\HSVtry2\\Reformatted_Data_Files')
#compile_movies('C:\\Users\\amschaef\\Documents\\HSVtry2\\Reformatted_Data_Files')
#filesearch('C:\\Users\\amschaef\\Documents\\HSV data')