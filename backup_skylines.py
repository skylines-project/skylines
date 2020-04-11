import os, sys, datetime, subprocess
import time as t
import paramiko

"""Ember server runs this script and saves to Nginx server, which saves to Google Drive
1. Database:  Keep nkeep dumps.  If the size of the current database is greater than the oldest dump, 
then delete the oldest dump.
2. htdocs:  Incremental: Add the igc files that are newer than the last backup to a new tar file.
"""

def dateFile(filename):
    return filename.split('.')[0].split('_')[1]

saveDir = '/home/bret/google_drive/'
htDir = '{}/htdocs'.format(saveDir)

nkeep = 3
timeFormat = '%Y-%m-%d.%H.%M.%S'

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
    nowStr = now.strftime("_{}".format(timeFormat))
    # print "Current date and time:",nowStr
    try:
        dumpFile = '/home/bret/servers/database-backups/skylinesdump{}.custom'.format(nowStr)
        os.system('sudo -u bret pg_dump --format=custom skylines > {}'.format(dumpFile))
    except:
        print 'error in pg_dump step'
    os.system('scp {} {}@{}:{}'.format(dumpFile,username,host,saveDir))
    try:
        files = ftp.listdir(saveDir)
        dumps = []
        dumpTimes = []
        dumpSizes = []
        for file in files:
            if 'dump' in file:
                try:
                    file.split('_')[1]>0
                    dumps.append(file)
                    dumpTimeStamp = file.split('_')[1].replace('.custom','')
                    dumpTimes.append(datetime.datetime.strptime(dumpTimeStamp, format(timeFormat)))
                    try:
                        size = ftp.stat('{}/{}'.format(saveDir, file)).st_size
                        # print 'test', file, size
                    except:
                        size = None
                    dumpSizes.append(size)
                    # print '{:.2f} MB, {}'.format(size / float(10 ** 6), file)
                except:
                    'skip file'
    except:
        print 'error in reading dumps'
    allInfo = zip(dumpTimes,dumps,dumpSizes)
    dumpsInfo =  [[dump,timeFile,size] for timeFile,dump,size in sorted(allInfo,reverse=True)] # name, timeFile, size
    for i in range(len(dumpsInfo)):
        file = dumpsInfo[i][0]
        size = dumpsInfo[i][2]
        print '{:.2f} MB, {}'.format(size / float(10 ** 6), file)
    oldestDump = dumpsInfo[-1]
    while len(dumpsInfo) > nkeep and oldestDump[2] <= dumpsInfo[0][2]: #Delete oldest if newest is larger or same size
        try: #delete oldest
            stdin, stdout, stderr = ssh.exec_command('rm {}/{}'.format(saveDir,oldestDump[0]))
            # Wait for the command to terminate
            while not stdout.channel.exit_status_ready() and not stdout.channel.recv_ready():
                t.sleep(1)
            stdoutstring = stdout.readlines()
            stderrstring = stderr.readlines()
            print 'Deleted', oldestDump[0]
            dumpsInfo.pop()
            oldestDump = dumpsInfo[-1]
        except:
            print 'Error in deleting oldest dump',oldestDump

    print
    t.sleep(5)


