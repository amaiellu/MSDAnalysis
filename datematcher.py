'''
Created on Oct 11, 2016

@author: amschaef
'''


import os
import xlwt

def datematcher(mydir):
    book=xlwt.Workbook()
    sheet1= book.add_sheet('Sheet 1')
    filenames=[]
    folder=[]
    i=0
    checkfiles=[]
    for root, dirs, files in os.walk(mydir):
        
        if files:
            os.chdir(os.path.join(root,'..'))
            q=os.getcwd()
            filenames=os.listdir(q)
            if filenames!=checkfiles:
                folder=os.path.basename(q)
                sheet1.write(i,0,folder)
                count=0
                for k in range(i,i+len(filenames)):
                    sheet1.write(i,1,filenames[count])
                    count=count+1
                    i=i+1
                    
                checkfiles=filenames
                
                
    os.chdir('C:\\Users\\amschaef\\Documents')   
    book.save('trial2.xls')  
    return

def dateinserter(mydir):
    for root, dirs, files in os.walk(mydir):
        
        if files:
            os.chdir(os.path.join(root,'..'))
            q=os.getcwd()
            filenames=os.listdir(q)
            folder=os.path.basename(q)
            print (folder)
            date=folder.split(' ')[1]
            donor=folder.split(' ')[0]
            for file in filenames:
                if len(date)>0:
                    if date not in file:
                        if donor in file:
                            loc=file.find(donor)
                            newfile=file[0:loc+4]+date+' '+file[loc+4:]
                            os.rename(file,newfile)
                        else:
                            newfile=donor+date+file
                            os.rename(file,newfile)
    return

def removethumbs(mydir):
    for root, dirs, files in os.walk(mydir):
        for file in files:
            if file.startswith('._Thumb'):
                os.remove(os.path.join(root,file))
                 
    return

def removeshifted(mydir):
    files=os.listdir(mydir)
    for file in files:
        if file.endswith('shift.csv') or file.endswith('ss.csv') or file.endswith('ms.csv'):
            os.remove(os.path.join(mydir,file))
    
    
    
    return
#removethumbs('E:\\Menstrual Cycle Study')
dateinserter('G:\\remaining MC Study vids')

#removeshifted('C:\\Users\\amschaef\\Documents\\HSVtry2')
