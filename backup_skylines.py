import os, sys, datetime, time
import paramiko

"""Ember server runs this script and saves to Nginx server, which saves to Google Drive
1. Database:  Keep nkeep dumps.  If the size of the current database is greater than the oldest dump, 
then delete the oldest dump.
2. htdocs:  Incremental: Add the igc files that are newer than the last backup to a new tar file.
"""

def dateFile(filename):
    return filename.split('.')[0].split('_')[1]

saveDir = 'bret@192.168.1.241:/home/bret/google_drive/'
htDir = '{}/htdocs'.format(saveDir)

nkeep = 3

#connection
host = '192.168.1.241'
port = 22
username = 'bret'
keyfile_path = '/home/bret/.ssh/id_rsa'
ssh = None
key = None
if 'dsa' in keyfile_path:
    key = paramiko.DSSKey.from_private_key_file(keyfile_path)
elif 'rsa' in keyfile_path:
    key = paramiko.RSAKey.from_private_key(open(keyfile_path,'r'))
else:
    sys.exit('Unknown key file type')
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(host, port, username, None, key)
ftp = ssh.open_sftp()
run = True
while run:
    now = datetime.datetime.now()
    nowStr = now.strftime("_%Y-%m-%d.%H.%M.%S")
    print("Current date and time:",nowStr)
    # automatically add keys without requiring human intervention
    try:
        files = ftp.listdir()
        print 'Files', files
        dumps = []
        for file in files:
            if 'dump' in file:
                dumps.append(file)
                print file
    except:
        print 'Error in ftp'

    time.sleep(5)


