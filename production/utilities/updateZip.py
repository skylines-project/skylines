# '''run in windows cmd window (no admin needed)
#         SET PATH=%PATH%;"C:\Program Files\7-Zip"
#         python d:\skylinesC\production\utilities\updateZip.py
#         
#         '''

import os,sys
import py7zr
import shutil

def readfile(filepath):
    with open(filepath) as f:
        lines = f.read().splitlines() #strips the lines of \n
    return lines

def sevenzip(tempPath,landPath):
    os.system('7z a -t7z "{}" "{}"'.format(tempPath,landPath)) #quotes to handle spaces in windows file names
#     with py7zr.SevenZipFile(tempPath, 'w') as archive:
#                     archive.writeall(landPath, 'base')  #This seems slow, but uses threads well

# mainDir = 'Z:\\temp'
# otherDir = 'Z:\\temp2'
mainDir = 'Z:\\Condor\\Landscapes'
otherDir = 'E:\\landscapes_for_symlinks'  #py7zr does not follow symlinks
zipDir = 'S:\\Skylines-C\landscapes-zip'

allLands = []
allLandPaths = []
allZips = []

#update symbolic links 
mainList = os.listdir(mainDir)
otherList = os.listdir(otherDir)
for item in otherList:
    if item not in mainList:
        print ('Updated symlink for {}.'.format(item))
        mainPath = '{}\\{}'.format(mainDir,item)
        otherPath = '{}\\{}'.format(otherDir,item)
        os.system('mklink /D "{}" "{}"'.format(mainPath,otherPath)) 

#landscapes
for item in os.listdir(mainDir):
    allLands.append(item)
    allLandPaths.append('{}\\{}'.format(mainDir,item))
    
for item in os.listdir(otherDir):
    if item not in allLands:
        allLands.append(item)
        allLandPaths.append(otherPath)
    
#zips
for item in os.listdir(zipDir):
    if item[-1]=='z':
        allZips.append('{}\{}'.format(zipDir,item)) 
        
#remove old temp zip files
for item in os.listdir(mainDir):
    if 'temp' in item:
        tempPath = mainDir+'\\{}'.format(item)
        os.remove(tempPath)
count = 0        
#create zips                
for i, landPath, in enumerate(allLandPaths):
    land = allLands[i]
#     print (land)
    iniPath = os.path.join(landPath,'{}.ini'.format(land))
    if os.path.exists(iniPath):
        lines = readfile(iniPath)
#         if len(lines) > 1:
        version = lines[1].split('=')[1].replace('00','0').replace('.10.','.1.')
#         else:
#             print ('lines', lines)
#             sys.exit('Stop: version line does not exist')
        zipPath = '{}\\{}.v{}.7z'.format(zipDir,land,version)
        if zipPath not in allZips and land != 'WestGermany3':
            print()
            print('----------------------------------------------------------')
            print(zipPath,)
            try:
                tempPath = mainDir+'\\temp_{}.7z'.format(land)
                sevenzip(tempPath,landPath)
                shutil.move(tempPath,zipPath)
                count += 1
            except:
                print ('Error creating {}'.format(zipPath))
              
    else:
        print('Skipping: {} does not exist'.format(iniPath))
print ('Done: moved {} zip files to {}'.format(count, zipDir))