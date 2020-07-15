"""Create symbolic links for each landscape folder stored outside the main Landscapes folder"""
import os, sys
mainDir = 'Z:\\Condor\\Landscapes'
otherDir = 'E:\\landscapes_for_symlinks'

mainList = os.listdir(mainDir)
otherList = os.listdir(otherDir)

for item in otherList:
    if item not in mainList:
        mainPath = '{}\\{}'.format(mainDir,item)
        otherPath = '{}\\{}'.format(otherDir,item)
        os.system('mklink /D "{}" "{}"'.format(mainDir,otherDir))
#         print ('Created symlink for {}'.format(item))
    elif  os.path.islink(mainPath):
#         os.system("deltree {}\\{}".format(otherDir,item))
        print('Please duplicate {} from {}'.format(otherDir))
        
        