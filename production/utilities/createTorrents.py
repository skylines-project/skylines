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

#find new zipped files
addTorrents  = []
for item in os.listdir(zipDir):
    oldLands.append(item.split('.'[0]))
    if item.split('.')[-1] == '7z':
        if not os.path.exists('{}/{}.torrent'.format(zipDir,item)):
            addTorrents.append(item)

#create torrents
tracker = 'http://tracker.opentrackr.org:1337/announcefile'
sizeExp = 21 # 2^21 bytes = 2MB
comment = 'skylinescondor.com'
for zipped in addTorrents:
    webSeed = 'http://199.192.98.227:8080/{}'.format(zipped)
    os.system('mktorrent -a {} -l {} -c {} -w {} {}'\
        .format(tracker,sizeExp,comment,webSeed,zipped))
    print '{}.torrent created'.format(zipped)
    # remove old versions of same landscape

#run update for skylinesC page.
os.system('python /home/bret/servers/repo-skylinesC/skylinesC/production/utilities/landscapes_page.py')
