import os,sys

def readfile(filepath):
    with open(filepath) as f:
        lines = f.read().splitlines() #strips the lines of \n
    return lines


mainDir = 'Z:\\Condor\\Landscapes'
# otherDir = 'E:\\landscapes_for_symlinks'  #already present in symlinks to mainDir
zipDir = 'S:\\Skylines-C\landscapes-zip'

allLands = []
allLandPaths = []
allZips = []

#landscapes
for item in os.listdir(mainDir):
    allLands.append(item)
    allLandPaths.append('{}\\{}'.format(mainDir,item))
    
#zips
for item in os.listdir(zipDir):
    if item[-1]=='z':
        allZips.append('{}\{}'.format(zipDir,item)) #leave out \ because used as string, not path
        
#create zips            
for i, path, in enumerate(allLandPaths):
    land = allLands[i]
#     print (land)
    iniPath = os.path.join(path,'{}.ini'.format(land))
    if os.path.exists(iniPath):
        lines = readfile(iniPath)
        if len(lines) > 1:
            version = lines[1].split('=')[1].replace('00','0').replace('.10.','.1.')
        else:
            print ('lines', lines)
            sys.exit('Stop: version line does not exist')
        zipPath = '{}\\{}.v{}.7z'.format(zipDir,land,version)
        if zipPath not in allZips and land != 'WestGermany3':
            print(zipPath)
            os.system('py7zr c {}  {}/'.format(zipPath,path))
        sys.exit('test1')
            
            
        
    else:
        sys.exit('Stop: {} does not exist'.format(iniPath))
        


print ('Done')