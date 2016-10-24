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
                
                if file.endswith(".csv") and not file.endswith('_tmp.csv'):
                    #os.rename(os.path.join(root,file),os.path.join(root,folder+'.csv'))
                    shutil.copy(os.path.join(root,file),'C:\\Users\\amschaef\\Documents\\Lai Lab\\Ebola in AM study')
                    

os.chdir('E:\\030116_AM')
attempt()