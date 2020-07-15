"""Creates symbolic links for each landscape folder stored outside the main Landscapes folder

Note python can't detect symlinks in Windows, so no easy way to check for duplicates.


"""
import os, sys
mainDir = 'Z:\\Condor\\Landscapes'
otherDir = 'E:\\landscapes_for_symlinks'

mainList = os.listdir(mainDir)
otherList = os.listdir(otherDir)

for item in otherList:
    print (item)
    
    if item not in mainList:
        mainPath = '{}\\{}'.format(mainDir,item)
        otherPath = '{}\\{}'.format(otherDir,item)
        os.system('mklink /D "{}" "{}"'.format(mainPath,otherPath))
        
        