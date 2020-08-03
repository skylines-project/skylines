# '''run in windows cmd window (no admin needed)
#         SET PATH=%PATH%;"C:\Program Files\7-Zip"
#         python d:\skylinesC\production\utilities\updateZipped.py
#
#         '''

import os,sys,time
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

mainDir = 'Z:\\Condor\\Landscapes'
otherDir = 'E:\\landscapes_for_symlinks'  #py7zr does not follow symlinks
zipDir = 'S:\\Skylines-C\landscapes-zip'

keepRunning = True
while keepRunning: #loops infinitely
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
        if 'WestGermany3' not in item:
            allLands.append(item)
            allLandPaths.append('{}\\{}'.format(mainDir,item))
    
    for item in os.listdir(otherDir):
        if item not in allLands:
            allLands.append(item)
            allLandPaths.append('{}\\{}'.format(otherDir, item))
    
    #zips
    for item in os.listdir(zipDir):
        if item.split('.')[-1] =='7z':
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
            if len(lines) > 1:
                version = lines[1].split('=')[1].split(',')[0].replace('00','0').replace('.10.','.1.')
            else:
                print ('lines', lines)
                sys.exit('Stop: version line does not exist')
            zipName = '{}.v{}.7z'.format(land.replace(' ','_'),version) #no zips will have spaces, but landscapes folders might
            zipPath = '{}\\{}'.format(zipDir,zipName) #no zips will have spaces, but landscapes folders might
            if zipPath not in allZips:
                print()
                print('----------------------------------------------------------')
                print(zipPath,)
                try:
                    #create new zip
                    landZip = zipPath.split('.')[0].split('\\')[-1]
                    tempPathZip = mainDir+'\\temp_{}.7z'.format(landZip)
                    print ('Creating {}'.format(zipName))
                    sevenzip(tempPathZip,landPath)
                    print('Moving to zip directory')
                    shutil.move(tempPathZip,zipPath)
                    count += 1
                except:
                    print ('Error creating {}'.format(zipPath))
    
        else:
            print('Skipping: {} does not exist'.format(iniPath))
    if count>0:
        print ('Moved {} zip files to {}'.format(count, zipDir))
    else:
        print ('No new landscapes to zip'.format(count, zipDir))
    time.sleep(60)
#loops infinitely


