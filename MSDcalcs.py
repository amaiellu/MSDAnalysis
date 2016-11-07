'''
Created on Aug 16, 2016

@author: amschaef
'''
import AnalysisPackage as ap
import pandas as pd
import numpy as np
import os
import shutil
import math 
import datetime

def MSDCalcs(mydir,expttag):

    files=os.listdir(mydir)
    
    files=[file for file in files if file.endswith('.xlsx')]
    files=[file for file in files if '~' not in file]
    anpath=os.path.join(mydir,'Analyzed Movies')
    if os.path.isdir(anpath)==False:
        os.mkdir(anpath)
    #our parameters---where will be set?
    frame_rate=15
    conversion=.156
    min_frames=5
    crittime=4/15
    # call functions
    count=0
    finpartDeff=pd.DataFrame(index=files, columns=['Total Particles', 'Avg Particles per Frame','Percent Mobile','Deff (t=0.2667s)'])
    finFrameMSD=pd.DataFrame(index=np.arange(0,40000), columns=files)
    logDeff05=pd.DataFrame(index=np.arange(0,len(np.arange(-7,3,.05))), columns=[files])
    logDeff1=pd.DataFrame(index=np.arange(0,len(np.arange(-7,3,.1))), columns=[files])
    logDeff25=pd.DataFrame(index=np.arange(0,len(np.arange(-7,3,.25))), columns=[files])   
    logDeff05.insert(0,'logDeff(10)',np.round(np.arange(-7,3,.05),decimals=2))
    logDeff1.insert(0,'logDeff(10)',np.round(np.arange(-7,3,.1),decimals=2))
    logDeff25.insert(0,'logDeff(10)',np.round(np.arange(-7,3,.25),decimals=2))
    
    for file in files:
        data=pd.read_excel(os.path.join(mydir,file),index_col=None,header=None,skiprows=[0],names=['particle','frame','x','y'],sheetname='Sheet1')
        if data.empty:
            print('The tracking file ' +file+' could not be loaded. The file is either empty, or is not formatted correctly.')
            finFrameMSD=finFrameMSD.drop(file,1)
            finpartDeff=finpartDeff.drop(file,0)
            logDeff05=logDeff05.drop(file,1)
            logDeff1=logDeff1.drop(file,1)
            logDeff25=logDeff25.drop(file,1)
        else: 
                     
            maxframe=data['frame'].max()
            time=pd.Series(ap.get_timescales(frame_rate,maxframe))
            blank_data=ap.insert_blanks(data)
            [filt_data,num_bad,avg_bad_frames,num_good,avg_good_frames]=ap.frame_filter(blank_data,min_frames)
        
            if filt_data.empty:
                print('There are no particles tracked for more than the minimum number of frames. Please check ' + file + ', or lower the minimum number of frames.')
                finFrameMSD=finFrameMSD.drop(file,1)
                finpartDeff=finpartDeff.drop(file,0)
                logDeff05=logDeff05.drop(file,1)
                logDeff1=logDeff1.drop(file,1)
                logDeff25=logDeff25.drop(file,1)
            else:
                #finData=ap.insert_blanks(filt_data)
                [MSD,Deff]=ap.calculate_MSD(filt_data,frame_rate,conversion,time)
                [num_stuck,avg_stuck_frames,MSD_stuck,XY_stuck,num_moving,avg_moving_frames,MSD_moving,XY_moving]=ap.MSD_classification(MSD, Deff, filt_data, min_frames, frame_rate, time,crittime)
                [edges,bins,percentages]=ap.dist(filt_data,5)
                #time=pd.Series(time)
                ap.format_sheets(MSD,time)
                
                ap.format_sheets(MSD_stuck,time)
                ap.format_sheets(MSD_moving,time)
        
                good_particles=pd.DataFrame({'Good Particles': num_good, 'Avg Frames':avg_good_frames},index=[' '])
                bad_particles=pd.DataFrame({'Bad Particles':num_bad,'Average Bad Frames':avg_bad_frames}, index=[' '])
                stuck_particles=pd.DataFrame({'Stuck Particles (logMSD<=-1.5)':num_stuck, 'Avg Stuck Frames': avg_stuck_frames},index=[' '])
                moving_particles=pd.DataFrame({'Moving Particles (logMSD>-1.5)':num_moving,'Avg Moving Frames': avg_moving_frames},index=[' '])
                histogram=pd.DataFrame({'# Frames':edges,'# Particles':bins,'% Particles': percentages})
        
        
        
            ##FRAME BY FRAME
                [fraction_moving,num_particles,log_Deffdist,A_deff,fbf_edges,frame_geom,avg_particles_frame]=ap.MSD_frame_by_frame(Deff,filt_data,MSD)
                
            ## Make Excel Sheets
                ap.format_sheets(Deff,time)
                ap.avg_format_sheets(frame_geom,time)
                fraction_moving=np.nan_to_num(fraction_moving)
                locations=np.asarray(num_particles)
                locations=np.where(locations>0)
                avg_percent_moving=np.average(fraction_moving[locations])*100
                avg_num_particles=np.average(num_particles)
                avg_logDeff_dist=log_Deffdist.iloc[locations].mean(axis=0)
                frame_by_frame=pd.DataFrame({'Frame #':np.arange(filt_data['frame'].min(),maxframe+1),'# Particles':np.asarray(num_particles),'% Moving':fraction_moving}, columns=['Frame #','# Particles','% Moving',' '])
                
                frame_by_frame_stats=pd.DataFrame({'Lables':['Average % Moving','Average # Particles'],'Values':[avg_percent_moving, avg_num_particles]})
                log_Deffdist.insert(0,'Frame',np.arange(filt_data['frame'].min(),maxframe+1))
                dist_header=pd.DataFrame(index=np.arange(0,2),columns=np.arange(1,len(fbf_edges)))
                dist_header.iloc[0]=pd.Series(fbf_edges)
                dist_header.iloc[1]=avg_logDeff_dist.values
                dist_header.insert(0,' ',['Edges','Averages'])
                time_header=pd.DataFrame(index=np.arange(0,1),columns=np.arange(0,2))
                time_header.iloc[0]=['Timescale',4/15]
        
        
        
        
            # write finished sheets
                filename=file.split('.')
                filename=filename[0]+'.xlsx'
                writer = pd.ExcelWriter(os.path.join(anpath,filename), engine='xlsxwriter')
                good_particles.to_excel(writer,sheet_name='Summary', startrow=1,index=False)
                bad_particles.to_excel(writer,sheet_name='Summary', startrow=4,index=False)
                stuck_particles.to_excel(writer,sheet_name='Summary', startrow=7,index=False)
                moving_particles.to_excel(writer,sheet_name='Summary', startrow=10,index=False)
                histogram.to_excel(writer,sheet_name='Summary', startrow=13,index=False)
                data.to_excel(writer,sheet_name='XY Original',index=False)
                filt_data.to_excel(writer,sheet_name='XY Good', index=False)
                XY_stuck.to_excel(writer,sheet_name='XY_Stuck', index=False)
                XY_moving.to_excel(writer,sheet_name='XY_Moving', index=False)
                MSD.to_excel(writer,sheet_name='MSD', index=False)
                MSD_stuck.to_excel(writer,sheet_name='MSD_Stuck', index=False)
                MSD_moving.to_excel(writer,sheet_name='MSD_Moving', index=False)
                Deff.to_excel(writer,sheet_name='Deff', index= False)
                A_deff.to_excel(writer,sheet_name='A_Deff',index=False)
                frame_by_frame.to_excel(writer,sheet_name='frame_by_frame stats',index=False)
                frame_by_frame_stats.to_excel(writer,sheet_name='frame_by_frame stats',index=False,header=False,startcol=4)
                time_header.to_excel(writer,sheet_name='frame by frame dist',index=False,header=False)
                dist_header.to_excel(writer,sheet_name='frame by frame dist',startrow=1,index=False,header=False)
                log_Deffdist.to_excel(writer,sheet_name='frame by frame dist',startrow=4,index=False)
                frame_geom.to_excel(writer,sheet_name='frame by frame MSD',index=False)
                writer.save()
                
                #master sheets
                finpartDeff['Total Particles'].iloc[count]=num_good
                finpartDeff['Avg Particles per Frame'].iloc[count]=avg_particles_frame
                finpartDeff['Percent Mobile'].iloc[count]=avg_percent_moving
                finpartDeff['Deff (t=0.2667s)' ].iloc[count]=Deff['Geom Mean'].iloc[3]
                finFrameMSD[file]=frame_geom['Geom Mean']
                avg_logDeff1=pd.Series(np.split(avg_logDeff_dist,math.floor(len(avg_logDeff_dist)/2)))
                avg_logDeff25=pd.Series(np.split(avg_logDeff_dist,math.floor(len(avg_logDeff_dist)/5)))
                avg_logDeff1=(avg_logDeff1.apply(lambda p:p.sum()))
                avg_logDeff25=(avg_logDeff25.apply(lambda p:p.sum()))
                ind05s=logDeff05[logDeff05['logDeff(10)']==fbf_edges[0]].index[0]
                ind05f=logDeff05[logDeff05['logDeff(10)']==fbf_edges[len(fbf_edges)-1]].index[0]
                ind1s=logDeff1[logDeff1['logDeff(10)']==fbf_edges[0]].index[0]
                ind1f=logDeff1[logDeff1['logDeff(10)']==fbf_edges[len(fbf_edges)-1]].index[0]
                ind25s=logDeff25[logDeff25['logDeff(10)']==fbf_edges[0]].index[0]
                ind25f=logDeff25[logDeff25['logDeff(10)']==fbf_edges[len(fbf_edges)-1]].index[0]
                logDeff05.loc[ind05s:ind05f-1,file]=avg_logDeff_dist.values
                logDeff05.loc[0:ind05s,file]=0
                logDeff1.loc[ind1s:ind1f-1,file]=avg_logDeff1.values
                logDeff1.loc[0:ind1s,file]=0
                logDeff25.loc[ind25s:ind25f-1,file]=avg_logDeff25.values
                logDeff25.loc[0:ind25s,file]=0
                
                print('completed'+file)
                count=count+1
                
                
    now=datetime.datetime.now()
    
    finalname='CompiledData'+' ' +expttag+' '+str(now.year) + str(now.month) + str(now.day) + ' '+str(now.hour) +str(now.minute) +str(now.second)+'.xlsx'    
    ap.format_sheets(finFrameMSD,time)       
    writer2 = pd.ExcelWriter(os.path.join(mydir,finalname), engine='xlsxwriter')    
    finpartDeff.to_excel(writer2,sheet_name='# Particles & Deff')    
    finFrameMSD.to_excel(writer2,sheet_name='Frame By Frame MSD')
    logDeff05.to_excel(writer2,sheet_name='logDeff Bin Size .05')
    logDeff1.to_excel(writer2,sheet_name='logDeff Bin Size .1')
    logDeff25.to_excel(writer2,sheet_name='logDeff Bin Size .25')
    writer2.save()
            
                
                
    return


MSDCalcs('C:\\Users\\amschaef\\Documents\\Lai Lab\\Ebola in AM study\\Reformatted_Data_Files\\Files For Check Tracking\\Links\\Compiled Movies\\compile 1','Ebola Tracing test')