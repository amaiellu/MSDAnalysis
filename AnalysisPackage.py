'''
Created on Jul 8, 2016

@author: amschaef
'''

#if __name__ == '__main__':
    #pass

import pandas as pd
import numpy as np
from scipy.stats.stats import gmean
from numpy import int, NaN,sqrt,diff,mean,array
from math import ceil,floor,log10
from blaze import nan
from scipy import NAN




def get_timescales(frame_rate,maxframe):
    timescales=np.array([x/frame_rate for x in range(1,maxframe+1)])
    return timescales

def calculate_MSD(particleData,frame_rate,conversion,timescales):
    #make dataframe for deff and msd
    maxframe=particleData['frame'].max()    
    #timescales=get_timescales(frame_rate,maxframe+1)
    
    #mean_disps=particleData.groupby('particle').apply(lambda p: get_diffs(p.x,p.y,conversion))
    MSD=particleData.groupby('particle').apply(lambda p: prep_fft_MSD(p.x,p.y,conversion))
    #xdisps=mean_disps.apply(lambda p: p[1])
    #ydisps=mean_disps.apply(lambda p: p[2])
    #xdisps=xdisps.apply(lambda p: p[~np.isnan(p)])
    #ydisps=ydisps.apply(lambda p: p[~np.isnan(p)])
    #count=xdisps.apply(lambda p: p.size)
    #MSD=mean_disps.apply(lambda p: p[1]+p[2]) 
    Deff=MSD.apply(lambda p: p/4/timescales[0:p.size])
    #MSDy=ydisps.apply(lambda p: (conversion**2)*np.cumsum(((p)**2)))
    #MSDx=MSDx/count
    #MSDy=MSDy/count
    #MSD=MSDx+MSDy
    #Deff=MSD/4
    #Deff=Deff.apply(lambda p: np.divide(p,timescales[0:p.size]))
  
    Deff=Deff.apply(lambda p: pd.Series(p))
    Deff=Deff.transpose()
    MSD=MSD.apply(lambda p: pd.Series(p))
    MSD=MSD.transpose()
        
    return MSD, Deff

def get_gmean(data): 
    
    datamat=data.as_matrix()
    
    gData=[]
    for i in range(0,len(datamat)):
        mat1=datamat[i]
        mat1=mat1[~np.isnan(mat1)]
        mat1=mat1[np.nonzero(mat1)]
        gData.append(gmean(mat1))
        
    gData=pd.Series(gData)
    
    return gData

def vel_mobility(velocities,threshold):
    
    q=velocities.groupby('particle')
    
    
    
    return

def frame_filter(data,min_frames):
    
    bad_data=data.groupby('particle').filter(lambda p: p.x.size<min_frames)
    filt_data = data.groupby('particle').filter(lambda p: p.x.size >=min_frames)
    num_good=filt_data['particle'].nunique()
    avg_good_frames=np.mean(filt_data.groupby('particle').apply(lambda p: p.x.size))
    num_bad=bad_data['particle'].nunique()
    avg_bad_frames=np.mean(bad_data.groupby('particle').apply(lambda p: p.x.size))
    
    
    return filt_data,num_bad,avg_bad_frames,num_good,avg_good_frames

def MSD_classification(MSD,Deff,data,min_frames,frame_rate,timescales,crittime):
         
        location=np.where(timescales==crittime)[0][0]
        critDeff=Deff.apply(lambda p: p[location] if p.size>location else p[p.size-1])
        cutoff=-1.5
        indices_stuck=critDeff[np.log10(critDeff)<cutoff].index
        if indices_stuck.size==0:
            num_stuck=0
            MSD_stuck=pd.DataFrame()
            XY_stuck=pd.DataFrame()
            avg_stuck_frames=0
        else:
            num_stuck=len(indices_stuck)
            MSD_stuck=MSD[indices_stuck]
            stuck_parts=[data[data['particle']==particle] for particle in indices_stuck]
            XY_stuck=pd.concat(stuck_parts)
            avg_stuck_frames=mean(XY_stuck.groupby('particle').apply(lambda p: p.x.size))
        
        indices_moving=critDeff[np.log10(critDeff)>=cutoff].index
        if indices_moving.size==0:
            num_moving=0
            MSD_moving=pd.DataFrame()
            XY_moving=pd.DataFrame()
            avg_moving_frames=0
        else:
            num_moving=len(indices_moving)
            MSD_moving=MSD[indices_moving]
            moving_parts=[data[data['particle']==particle] for particle in indices_moving]
            XY_moving=pd.concat(moving_parts)
            avg_moving_frames=mean(XY_moving.groupby('particle').apply(lambda p: p.x.size))
            
       
        return num_stuck,avg_stuck_frames,MSD_stuck,XY_stuck,num_moving,avg_moving_frames,MSD_moving,XY_moving

def dist(pdata,bin_unit):
    counts=pdata.groupby('particle').apply(lambda p: p.frame.size)
    edges=np.arange(0,pdata['frame'].max()+2*bin_unit,bin_unit)
    bin_edge=0
    i=0
    bins=[]
    while i<len(edges)-1:
       bins.append(np.compress((edges[i] <= counts.as_matrix()) & (counts.as_matrix() < edges[i+1]), counts).size)
       i+=1
    percentages=np.multiply(np.divide(bins,sum(bins)),100)
    edges=np.delete(edges,len(edges)-1)

    return edges,bins,percentages

def very_deep_copy(self):
    copy=pd.DataFrame(self.values.copy(), self.index.copy(), self.columns.copy())
    copy['particle']=copy[['particle']].astype(int)
    copy['frame']=copy[['frame']].astype(int)
    return copy

def format_sheets(sheet,time):
           
        
        sheet.insert(0,'Geom Mean',get_gmean(sheet))
        sheet.insert(0,'Timescales',time[0:sheet.shape[0]])
        sheet.insert(2,' ',pd.Series())
    
def calc_velocity(data,frame_rate,conversion):
    from numpy import diff,sum,mean,sqrt
    disps=data.groupby('particle').apply(lambda p:(sqrt(diff(p.x)**2+diff(p.y)**2)))*conversion
    avg_per_frame=disps.apply(lambda p:mean(p))
    avg_per_frame=mean(avg_per_frame)
    totdisps=disps.apply(lambda p:sum(p))
    pathsize=data.groupby('particle').apply(lambda p: p.x.size)/15
    arc_velocity=totdisps/pathsize
    arc_velocity=pd.Series(arc_velocity,index=data['particle'].unique())
    
    return arc_velocity,avg_per_frame

def insert_blanks(data):
    #code to insert blanks between non continuous frames of the same particle
    from operator import itemgetter
    import itertools as it
    finData=pd.DataFrame(columns=['particle','frame','x','y'])
    particles=data['particle'].unique()
    for particle in particles:
        indData=data[data['particle']==particle]
        framelist=indData['frame'].values.ravel()
        groups=np.split(framelist, np.where(np.diff(framelist) != 1)[0]+1)
        for group in range(0,len(groups)):
           if group<len(groups)-1:
                end=groups[group+1][0]
                start=groups[group][len(groups[group])-1]
                gap=end-start-1
                blanks=pd.DataFrame(columns=['particle','frame','x','y'],index=np.arange(0,gap))
                blanks['particle']=particle
                blanks['frame']=np.arange(start+1,end)
                startslice=indData[indData['frame']==groups[group][0]].index
                endslice=indData[indData['frame']==groups[group][len(groups[group])-1]].index                                                 
                finData=pd.concat([finData,indData.iloc[startslice[0]:endslice[0]+1]], axis=0, ignore_index=True)
                finData=pd.concat([finData,blanks],axis=0,ignore_index=True)
           elif group==len(groups)-1:
                startslice=indData[indData['frame']==groups[group][0]].index
                endslice=indData[indData['frame']==groups[group][len(groups[group])-1]].index 
                finData=pd.concat([finData,indData.loc[startslice[0]:endslice[0]+1]], axis=0, ignore_index=True)
             
    return finData

def velocity_classification(finData):
    #use combination of speed and max displacement,return time metric as discussed with Jay
    # greater than 4.7
    
    
    
    tdm = finData.groupby('particle').filter(lambda p: mean(sqrt(diff(p.x)**2 + diff(p.y)**2)) > 4.68
            or sqrt((array(p.x)[-1]-array(p.x)[0])**2 + (array(p.y)[-1]-array(p.y)[0])**2) > 5)
    
       
    num_moving_frames=tdm.shape[0]
    num_frames=finData.shape[0]
    
    num_moving=tdm['particle'].nunique()
    num_particles=finData['particle'].nunique()
    
    percent_moving=num_moving/num_particles
    time_moving=num_moving_frames/num_frames
      
    return percent_moving,time_moving

def drift_velocity(data,maxdisps,conversion,frame_rate):
    #help class swimming or non-swimming
    particles=data['particle'].unique()
    drift_vs=[]
    num_frames=data.groupby('particle').apply(lambda p: p.x.size)
    drift_v=maxdisps/num_frames
    drift_v=drift_v*conversion/frame_rate

    
        
    return drift_v

def renumber(data):
    particles=data['particle'].unique()
    count=0;
    for particle in particles:
        data['particle'][data['particle']==particle]=count
        count=count+1
    
    return data

def max_displacement(data,conversion):
    disps = data.groupby('particle').apply(lambda p: sqrt((array(p.x)[-1]-array(p.x)[0])**2 + (array(p.y)[-1]-array(p.y)[0])**2))
    disps=disps*(conversion)
    return disps

def MSD_frame_by_frame(Deff,filt_data,MSD):
    max_frame=filt_data['frame'].max()
    A_deff=pd.DataFrame({'particle':filt_data['particle'],'frame':filt_data['frame'],'Deff': pd.Series()}, columns=['particle','frame','Deff'])
    timeDeff=Deff.iloc[3]
    particles=A_deff['particle'].unique()
    
    for i in range(0,len(particles)):
        A_deff['Deff'].loc[A_deff['particle']==int(particles[i])]=timeDeff[int(particles[i])]
        

    lower_edge= floor(log10(min(A_deff['Deff'].iloc[np.nonzero(A_deff['Deff'])])))
    upper_edge= ceil(log10(max(A_deff['Deff'].iloc[np.nonzero(A_deff['Deff'])]))) 
    num_edge=(upper_edge-lower_edge)/.05 +1
    fbf_edges=np.linspace(start=lower_edge,stop=upper_edge,num=num_edge)
    num_particles=[]
    fraction_moving=[]
        
    num_particles_frame=A_deff.groupby('frame').apply(lambda p: ((np.isnan(p.Deff))==False).sum())
    num_frame_moving=A_deff.groupby('frame').apply(lambda p: ((np.log10(p.Deff)>=-1.5)==True).sum())
    fraction_moving=num_frame_moving/num_particles_frame
    spread=A_deff.groupby('frame').apply(lambda p: np.histogram(np.log10(p.Deff),bins=fbf_edges)[0])
    logDeffdist=spread.apply(lambda p : pd.Series( p/sum(p)*100))
    
    num_particles_frame=filt_data.groupby('frame').apply(lambda p: ((np.isnan(p.particle))==False).sum())
    avg_particles_frame=mean(num_particles_frame)
    
    
    hist=filt_data.groupby('particle').apply(lambda p: p.x.size )
    hist=np.histogram(hist.values,bins=np.arange(0,max_frame+5,5))[0]
    hist=pd.DataFrame(data={'Num Particles':hist,'Frames':np.arange(0,max_frame,5)},columns=['Frames','Num Particles'])
    
    MSD_frame=MSD.drop(MSD.columns[[0,1,2]],axis=1)
    ind_particles_frame=A_deff.groupby('frame').apply(lambda p: get_gmean(MSD_frame[p.particle.values]))
    frame_geom=ind_particles_frame.transpose()
  
   
    return fraction_moving,num_particles_frame,logDeffdist,A_deff,fbf_edges,frame_geom,avg_particles_frame

def msd_fft(r):
    
    N=len(r)
    D=np.square(r).sum(axis=1) 
    D=np.append(D,0) 
    S2=sum([autocorrFFT(r[:, i]) for i in range(r.shape[1])])
    Q=2*D.sum()
    S1=np.zeros(N)
    for m in range(N):
        Q=Q-D[m-1]-D[N-m]
        S1[m]=Q/(N-m)
    msds=S1-2*S2
    
    return msds[1:]

def autocorrFFT(x):
    N=len(x)
    F = np.fft.fft(x, n=2*N)  #2*N because of zero-padding
    PSD = F * F.conjugate()
    res = np.fft.ifft(PSD)
    res= (res[:N]).real   #now we have the autocorrelation in convention B
    n=N*np.ones(N)-np.arange(0,N) #divide res(m) by (N-m)
    return res/n #this is the autocorrelation in convention A

def abs_velocities(data,conversion,timescales):
    mean_disps=data.groupby('particle').apply(lambda p: get_diffs(p.x,p.y,conversion))
    velocities=mean_disps.apply(lambda p: pd.Series(p*conversion/timescales[0:len(p)]))
    velocities=velocities.transpose()
    
    
    return velocities

def vel_frame_by_frame(filt_data,velocities,maxdisps,threshold):
        
    max_frame=filt_data['frame'].max()    
    
    hist=filt_data.groupby('particle').apply(lambda p: p.x.size )
    hist=np.histogram(hist.values,bins=np.arange(0,max_frame+5,5))[0]
    hist=pd.DataFrame(data={'Num Particles':hist,'Frames':np.arange(0,max_frame,5)},columns=['Frames','Num Particles'])
    
    num_particles_frame=filt_data.groupby('frame').apply(lambda p: ((np.isnan(p.particle))==False).sum())
    avg_particles_frame=mean(num_particles_frame)
    
    velocities_by_frame=filt_data.groupby('frame').apply(lambda p: get_gmean(velocities[p.particle.values]))
    velocities_by_frame=velocities_by_frame.transpose()
    
    num_particles=filt_data.groupby('frame').apply(lambda p: p.particle.nunique())
    thresholds=[.25,.5,1,2,3,4,5,6,7,8,9,10]
    num_particles_moving=pd.DataFrame(index=np.arange(0,filt_data['frame'].max()), columns=thresholds)
    for threshold in thresholds:
        fract_moving=filt_data.groupby('frame').apply(lambda p: ((velocities[p.particle.values].iloc[3]>=threshold)==True).sum())
        fract_moving=fract_moving/num_particles
        num_particles_moving[threshold]=fract_moving
    num_particles_moving=num_particles_moving.mean(axis=0)    
    disps=max_displacement(filt_data,.156)
    dist_thresh=np.arange(.1,7,.1)
    particles=filt_data.groupby('particle').filter(lambda p: p.x.size>=50)
    particles=particles['particle'].unique()
    num_dist_mov=pd.DataFrame(index=np.arange(0,filt_data['frame'].max()), columns=dist_thresh)
    for i in range(0,len(dist_thresh)):
        stuck=[]
        for j in range(0,len(particles)):
            if disps.iloc[particles[j]]<dist_thresh[i]:
                stuck=np.append(stuck,particles[j])
        numStuckFrame=pd.Series(index=np.arange(0,filt_data['frame'].max()+1))
        for k in range(0,filt_data['frame'].max()+1): 
            indFrame=filt_data[filt_data['frame']==k]
            particlesFrame=indFrame['particle'].unique()
            tr=np.in1d(stuck,particlesFrame)
            numStuckFrame.iloc[k]=1-(np.sum(tr)/num_particles_frame)
            
        num_dist_mov[dist_thresh[i]]=numStuckFrame
        num_dist_mov=num_dist_mov.mean(axis=0)
        
    
    #fraction_moving=num_particles_moving/num_particles
    #fraction_dist_moving=num_dist_moving/num_particles
    #fraction_moving=mean(fraction_moving)
    #fraction_dist_moving=mean(fraction_dist_moving)
    return avg_particles_frame,hist,velocities_by_frame,num_particles_moving,num_dist_mov


def get_diffs(particlex,particley,conversion):
    mean_dispsx=[]
    mean_dispsy=[]
    MSDx=[]
    MSDy=[]
    for i in range(0,len(particlex)-1):
        zeroes=np.zeros(i+1)
        dispsx=np.subtract(particlex.values,np.append(particlex[i+1:len(particlex)].values,zeroes))
        dispsx=dispsx[0:len(dispsx)-len(zeroes)]
        dispsx=dispsx[~np.isnan(dispsx)]
        count=len(dispsx)
        MSDx=np.append(MSDx,conversion**2*np.sum(dispsx**2)/count)
        mean_dispsx=np.append(mean_dispsx,mean(abs(dispsx)))
        
        dispsy=np.subtract(particley.values,np.append(particley[i+1:len(particley)].values,zeroes))
        dispsy=dispsy[0:len(dispsy)-len(zeroes)]
        dispsy=dispsy[~np.isnan(dispsy)]
        MSDy=np.append(MSDy,conversion**2*np.sum(dispsy**2)/count)
        mean_dispsy=np.append(mean_dispsy,mean(abs(dispsy)))
   
    mean_disps=np.sqrt(mean_dispsx**2+mean_dispsy**2)    
    return mean_disps,MSDx,MSDy

def prep_fft_MSD(x,y,conversion):
    x=np.asarray(x)*conversion
    y=np.asarray(y)*conversion
    path=np.dstack((x,y))[0]
    return msd_fft(path)