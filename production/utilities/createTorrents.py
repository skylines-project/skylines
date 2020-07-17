# Options:
# -a <url>[,<url>]* : specify the full announce URLs
#                     at least one is required
#                     additional -a adds backup trackers
# -c <comment>      : add a comment to the metainfo
# -d                : don't write the creation date
# -h                : show this help screen
# -l <n>            : set the piece length to 2^n bytes,
#                     default is 18, that is 2^18 = 256kb
# -n <name>         : set the name of the torrent,
#                     default is the basename of the target
# -o <filename>     : set the path and filename of the created file
#                     default is <name>.torrent
# -p                : set the private flag
# -s                : add source string embedded in infohash
# -v                : be verbose

import os, sys

zipDir = '/media/sf_landscapes-zip/'
workDir = zipDir
os.chdir(workDir)

# zipDirList = os.listdir(zipDir)
#find new zipped files
zippedForTorrent  = []
oldZipped = []

for item in zipDirList:
    
    if item.split('.')[-1] == '7z':
        oldZipped.append(item)
        if not os.path.exists('{}/{}.torrent'.format(zipDir,item)):
            zippedForTorrent.append(item)
        else:
            oldZipped.append(item)

#create torrents
tracker = 'http://tracker.opentrackr.org:1337/announcefile'
sizeExp = 21 # 2^21 bytes = 2MB
comment = 'skylinescondor.com'
for zipped in zippedForTorrent:
    webSeed = 'http://199.192.98.227:8080/{}'.format(zipped)
    os.system('mktorrent -a {} -l {} -c {} -w {} {}'\
        .format(tracker,sizeExp,comment,webSeed,zipped))
    print ('{}.torrent created'.format(zipped))
    # remove old version files with same landscape
    land = zipped.split('.')[0]
    for item in oldZipped:
        if item.split('.')[0] == land:
            zipVersion = '{}/{}'.format(zipDir,item)
            os.remove(zipVersion)
            print ('removed',zipVersion)
            torrentVersion = '{}/{}.torrent'.format(zipDir,item)
            if os.path.exists(torrentVersion):
                os.remove(torrentVersion)
                print ('removed',torrentVersion)
            
#run update for skylinesC page.
os.system('python /home/bret/servers/repo-skylinesC/skylinesC/production/utilities/landscapes_page.py')