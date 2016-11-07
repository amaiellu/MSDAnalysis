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
from scipy import NAN

def compile_movies(mydir):
    
    compilepath=os.path.join(mydir,'Compiled Movies')
    for dirpaths, dirnames, filenames in os.walk(mydir):
        if not dirnames:
            XY_all=pd.DataFrame(columns=['particle','frame','x','y'])
            for file in filenames:
                if file.endswith('.xlsx'):
                    this_movie=pd.read_excel(os.path.join(dirpaths,file),header=None,names=['particle','frame','x','y'],sheetname='Sheet1')
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
            basename=basename.replace('(final)','')
            if '(' in basename:
                basename=basename[0: len(basename)-5]
                    
            else:
                basename=basename[0:len(basename)-4]
            if os.path.isdir(os.path.join(dirpaths,basename))==False:
                    os.mkdir(os.path.join(dirpaths,basename))
            
            shutil.move(os.path.join(dirpaths,file),'\\\\?\\'+os.path.abspath(os.path.join(dirpaths,basename)))
            
    return

def tracelink(mydir,conversion,cutoff):
#    if os.path.isdir(os.path.join(mydir,'Links'))==False:
        #os.mkdir(os.path.join(mydir,'Links'))
    files=os.listdir(mydir)
    files=files
    for file in files:
        data=pd.read_excel(os.path.join(mydir,file),header=None,names=['particle','frame','x','y'],sheetname='Sheet1')
        exits=data.groupby('particle', as_index=False).apply(lambda p: p.tail(1))
        exits=exits.groupby('particle', as_index=False).filter(lambda p: p.frame.values[0]<301) #find all particle exits. 301 is the last frame, so nothing will be joined after this
        particles=exits['particle'].unique() #list of unique particles to check for links
        entries=data.groupby('particle').apply(lambda p: p.iloc[0]) 
        entries=entries.groupby('particle',as_index=False).filter(lambda p: p.frame.values[0]>2 ) #find all entry points for particles. if it enters in the first frame, it won't be linked to anything prior
        entries.sort_values('frame',inplace=True) # make sure the entries are in order, as we will stop after the closest match is found
        #matches=pd.DataFrame(index=np.arange(0,len(entries)*len(exits)),columns=['exit particle','exit frame', 'matched particle', 'matched frame', 'distance','msd'])
        #count=0
        for i in range (0,len(particles)): # loop through each particle exit
            
            inddata=exits.iloc[i]  # get current exit
            #exit_part=inddata['particle']
            subset_entries=entries[entries['frame'].values>inddata['frame']]# get list of particles that enter after this one exits
            for j in range (0,subset_entries.shape[0]): # go through all entries
                entry=subset_entries.iloc[j] # get current entry
                msd=conversion**2*((entry['x']-inddata['x'])**2+(entry['y']-inddata['y'])**2) # calculate distance requirement
                if msd<cutoff: # check if it is a match
                    #matches['exit particle'].iloc[count]=exit_part
                    #matches['exit frame'].iloc[count]=inddata['frame']
                    #matches['matched particle'].iloc[count]=entry['particle']
                    #matches['matched frame'].iloc[count]=entry['frame']
                    #matches['distance'].iloc[count]=entry['frame']-inddata['frame']
                    #matches['msd'].iloc[count]=msd
                    #count=count+1
                    #matches['matched particle'][matches['exit particle']==exit_part]=np.append(matches['matched particle'][matches['exit particle']==exit_part],entry['particle'])
                    #matches['matched frame'][matches['exit particle']==exit_part]=np.append(matches['matched frame'][matches['exit particle']==exit_part],entry['frame'])
                    #matches['distance'][matches['exit particle']==exit_part]=np.append(matches['distance'][matches['exit particle']==exit_part],entry['frame']-inddata['frame'])
                    #matches['msd'][matches['exit particle']==exit_part]=np.append(matches['msd'][matches['exit particle']==exit_part],msd)
                    droppart=entry['particle'] # particle must be removed from list of entries so we don't match it to some other particle later
                    entries=entries.drop(droppart) # drop the particle from entries
                    if len(exits[exits['particle']==droppart])>0: #if the entry particle that was just linked is in the list of exits, we have to update the particleid
                        id=exits[exits['particle']==droppart].index.labels[0][0] 
                        exits.loc[id,'particle']=exits.iloc[i].particle # now any future exit has that particle number
                    ind=data[data['particle']==droppart].index   # find location of linked particle in original dataframe 
                    data.loc[ind,'particle']=exits.iloc[i].particle #link the particles together in the original dataframe 
                    
                    break # stop looking for matches to this particle
        #matches.sort_values(['exit particle','msd'], inplace=True)
        #q=matches.groupby('exit particle').apply(lambda p: min(p.msd) )
        #minmatches=matches.iloc[q.index]
        #matches[np.isfinite(matches['matched particle']).values]
        #i=0
        #while i < matches.shape[0]:
        #    indData=matches.iloc[i]
            
        #    if np.isfinite(indData['matched particle']) and indData['matched particle'] in data['particle']:
        #        droppart=indData['matched particle']
        #        indexes=matches[matches['exit particle']==indData['exit particle']].index
                #i=i+len(matches[matches['exit particle']==indData['exit particle']])
                #matches=matches[matches['exit particle']!=indData['exit particle']]
        #        matches['exit particle'][matches['exit particle']==droppart]=indData['exit particle']
        #        ind=data[data['particle']==droppart].index 
        #        end=max(indexes)
        #        i=end
        #        data.loc[ind,'particle']=indData['exit particle']
        #    i=i+1        
        data.sort_values(['particle','frame'],inplace=True)
        writer=pd.ExcelWriter(os.path.join(mydir,'links '+file), engine='xlsxwriter')
        data.to_excel(writer,sheet_name='Sheet1',index=False)   
        writer.save()
        print('completed ' + file)
        #shutil.move(os.path.join(mydir,file),'C:\\Users\\amschaef\\Documents\\Lai Lab\\Ebola in AM study\\Reformatted_Data_Files\\Files For Check Tracking\\done')
        
    return
    
def find_ent(particle,entries,conversion,cutoff):    
    comp_entries=entries.groupby('particle').filter(lambda q: q.frame.values[0]>particle.frame.values[0])
    comp_entries=comp_entries.groupby('particle').filter(lambda q: conversion**2*((q.x.values[0]-particle.x.values[0])**2+(q.y.values[0]-particle.y.values[0])**2)<cutoff)
    dist=comp_entries.groupby('particle').apply(lambda q: q.frame.values[0]-particle.frame.values[0])
    if len(dist)>0:
        min_particle=dist.argmin()
        return min_particle
    else:
        return NAN
    
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
def shift_check(dir):
    
    return

    
#compile_movies('C:\\Users\\amschaef\\Downloads\\no linking\\Individual Movie XY Data')
#fixfiles('C:\\Users\\amschaef\\Documents\\Lai Lab\\Ebola in AM study\\Reformatted_Data_Files\\Files For Check Tracking\\Links')
#compile_movies('C:\\Users\\amschaef\\Documents\\Lai Lab\\Ebola in AM study\\Reformatted_Data_Files\\Files For Check Tracking\\Links')
#filesearch('C:\\Users\\amschaef\\Documents\\HSV data')