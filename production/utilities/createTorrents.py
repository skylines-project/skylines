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
addTorrents  = []
print os.listdir(zipDir)

#find new zip files
for item in os.listdir(zipDir):
    if item.split('.')[-1] == '7z':
        if not os.path.exists('{}/{}.torrent'.format(zipDir,item)):
            addTorrents.append(item)
#create torrents
tracker = 'http://tracker.opentrackr.org:1337/announcefile'
sizeExp = 21 # 2^21 bytes = 2MB
comment = 'skylinescondor.com'
for zip in addTorrents:
    webSeed = 'http://199.192.98.227:8080/{}'.format(zip)
    os.system('mktorrent -a {} -l {} -c {} -w {} {}'\
        .format(tracker,sizeExp,comment,webSeed,zip))
    print '{}.torrent created'.format(zip)


