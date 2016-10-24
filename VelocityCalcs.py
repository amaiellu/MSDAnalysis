'''
Created on Aug 16, 2016

@author: amschaef
'''
import AnalysisPackage as ap
import pandas as pd
import numpy as np
import math as m
import os 
def velocityCalcs(mydir):

        frame_rate=15
        conversion=.156
        min_frame=5
        threshold=.9*4.59
        files=os.listdir(mydir)
        anpath=os.path.join(mydir,'Analyzed Movies')
        if os.path.isdir(anpath)==False:
            os.mkdir(anpath)
        
        
        vel_mov=pd.DataFrame(index=files,columns=[.25,.5,1,2,3,4,5,6,7,8,9,10])
        dist_mov=pd.DataFrame(index=files, columns=np.arange(.1,7,.1))
        finvelocities=pd.DataFrame(index=np.arange(0,40000), columns=files)
        finframes_vs=pd.DataFrame(index=np.arange(0,40000), columns=files)
        #finmobility=pd.DataFrame(index=files, columns=['Fraction Time','Percent by Particle'])
        finavg_per_frames=pd.DataFrame(index=files, columns=['Total Particles', 'Avg Particles per Frame','Percent Mobile'])
        count=0
        
        for file in files:
            data=pd.read_excel(os.path.join(mydir,file),header=None, index_col=0, skiprows=[0],names=['particle','frame','x','y'])
            maxframe=data['frame'].max()
            timescales=ap.get_timescales(frame_rate,maxframe)
            [filt_data,num_bad,avg_bad_frames,num_good,avg_good_frames]=ap.frame_filter(data,min_frame)
            velocities=ap.abs_velocities(filt_data,conversion,timescales)
           
            
            #velocities,avg_per_frame=ap.calc_velocity(filt_data, frame_rate, conversion)
            maxdisps=ap.max_displacement(filt_data)
            #drift_vs=ap.drift_velocity(filt_data, maxdisps, conversion, frame_rate)
            [percent_moving, time_moving]=ap.velocity_classification(filt_data)
            
            [avg_particles_frame,hist,velocities_by_frame,vel_based_mov,dist_based_mov]=ap.vel_frame_by_frame(filt_data,velocities,maxdisps,threshold)
            ap.format_sheets(velocities_by_frame,timescales)
            ap.format_sheets(velocities,timescales)
            vel_mov.iloc[count]=vel_based_mov.values
            dist_mov.iloc[count]=dist_based_mov.values
            #Output Sheets
            
            #XY Orgnal
            #XY Final
            #Arc Velocities
            #Drift Velocitites
            #Total Displacements
            #Percent moving by partice, time movng by frame
            #mobility=pd.DataFrame(data={'Percent Moving by Particle': pd.Series(percent_moving),'Fraction Time Moving':pd.Series(time_moving)})
            #drift_vs=pd.DataFrame(data={'Particle':np.arange(0,len(drift_vs)),'Drift_Velocities':drift_vs.values},columns=['Particle','Drift_Velocities'])
            #maxdisps=pd.DataFrame(data={'Particle':np.arange(0,len(maxdisps)),'Displacements (pixels)':maxdisps}, columns= ['Particle','Displacements (pixels)'])
            #velocities=pd.DataFrame(data={'Particle':np.arange(0,len(velocities)),'Arc Velocities (um/s)': velocities.values},columns = ['Particle','Ind Particles Velocities (um/s)'])
            #avg_per_frame=pd.DataFrame(data={'Pixels per frame':pd.Series(avg_per_frame)},columns=['Pixels per frame'])
            
            filename=file.split('.')
            filename=filename[0]+'.xlsx'
            writer = pd.ExcelWriter(os.path.join(anpath,filename), engine='xlsxwriter')
            #data.to_excel(writer,sheet_name='XY Original',index=0)
            #filt_data.to_excel(writer,sheet_name='XY Final',index=0)
            #velocities.to_excel(writer, sheet_name='Arc Velocities',index=0)
            #drift_vs.to_excel(writer,sheet_name='Drift Velocities',index=0)
            #maxdisps.to_excel(writer, sheet_name='Particle Displacements',index=0)
            #mobility.to_excel(writer,sheet_name='Mobility Ratios',index=0)
            #avg_per_frame.to_excel(writer,sheet_name='Avg Pixels per Frame',index=0)
            
            
            #finmobility.iloc[count]=mobility.values        
            finavg_per_frames.iloc[count]=[num_good,avg_particles_frame,'pass']#,#fraction_moving]
            finvelocities[file]=velocities['Geom Mean']
            finframes_vs[file]=velocities_by_frame['Geom Mean']
            
            
    
        
            good_particles=pd.DataFrame({'Good Particles': num_good, 'Avg Frames':avg_good_frames,'Avg Particles per Frame':avg_particles_frame},index=[' '])
            bad_particles=pd.DataFrame({'Bad Particles':num_bad,'Average Bad Frames':avg_bad_frames}, index=[' '])
            velocities.to_excel(writer,sheet_name='Ind Particle Velocities',index=0)
            velocities_by_frame.to_excel(writer,sheet_name='Frame-by-Frame Velocities',index=0)
            good_particles.to_excel(writer,sheet_name='Summary', startrow=1,index=False)
            bad_particles.to_excel(writer,sheet_name='Summary', startrow=4,index=False)
      
        #stuck_particles.to_excel(writer,sheet_name='Summary', startrow=7,index=False)
        #moving_particles.to_excel(writer,sheet_name='Summary', startrow=10,index=False)
            hist.to_excel(writer,sheet_name='Summary', startrow=13,index=False)
            data.to_excel(writer,sheet_name='XY Original',index=False)
            filt_data.to_excel(writer,sheet_name='XY Good', index=False)
        #XY_stuck.to_excel(writer,sheet_name='XY_Stuck', index=False)
        #XY_moving.to_excel(writer,sheet_name='XY_Moving', index=False)
        #finvelocities.to_excel(writer, sheet_name='Arc Velocities',index=0)
        #findrift_vs.to_excel(writer,sheet_name='Drift Velocities',index=0)
        #finmobility.to_excel(writer,sheet_name='Mobility Ratios')
        #finavg_per_frames.to_excel(writer,sheet_name='Avg Pixels per Frame')
            writer.save()
            print('completed'+file)
            count=count+1
        
        #write masterfile
        writer2 = pd.ExcelWriter(os.path.join(mydir,'Salmonella.xlsx'), engine='xlsxwriter')
        vel_mov.to_excel(writer2, sheet_name='Velocity Based Thresholds')
        dist_mov.to_excel(writer2,sheet_name='Distance Based Moves')
        finframes_vs.to_excel(writer2,sheet_name='Ind Particle Velocities')
        finvelocities.to_excel(writer2,sheet_name='Frame by Frame Velocities')
        finavg_per_frames.to_excel(writer2, sheet_name='Summary')
        writer2.save()
        
        
        
        
        return   


velocityCalcs('C:\\Users\\amschaef\\Downloads\\salm3')
