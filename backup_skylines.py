import os, sys, datetime, subprocess
import time as t
import paramiko
import tarfile

"""Ember server runs this script and saves to Nginx server, which saves to Google Drive
1. Database:  Keep nkeep dumps.  If the size of the current database is greater than the oldest dump, 
then delete the oldest dump.
2. htdocs:  Incremental: Add the igc files that are newer than the last backup to a new tar file.
"""

# def dateFile(filename):
#     return filename.split('.')[0].split('_')[1]

saveDir = '/home/bret/google_drive'
igcsInDir = '/home/bret/servers/repo-skylinesC/skylinesC/htdocs/files'
dbBUdir = '/home/bret/servers/database_backups'
igcsOutDir = '{}/igcsDir'.format(saveDir)

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
files = ftp.listdir(saveDir)
run = True
while run:
    # close port 4200 so can't write new data while backing up
    os.system('sudo ufw deny 4200')
    now = datetime.datetime.now()
    nowStr = now.strftime("_{}".format(timeFormat))
    #### Database backup #####
    if True: #debugging switch, when working on tar section below
        try:
            dumpFile = '{}/skylinesdump{}.custom'.format(dbBUdir,nowStr)
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

    #### htdocs igcs backup #####
    # Read date of last htdocs tar file in saveDir

    if not igcsOutDir.split('/')[-1] in files:
        ftp.mkdir(igcsOutDir)
    try:
        filesIGC = ftp.listdir(igcsOutDir)
    except:
        print 'error in reading tars'
    tars = []
    tarTimes = []
    tarSizes = []
    for file in filesIGC:
        if 'tar' in file:
            try:
                file.split('_')[1] > 0
                tars.append(file)
                tarTimeStamp = file.split('_')[1].split('-backto-')[0]  #.replace('.tar.gz', '')
                size = ftp.stat('{}/{}'.format(igcsOutDir, file)).st_size
                tarSizes.append(size)
                tarTimes.append(datetime.datetime.strptime(tarTimeStamp, format(timeFormat)))
            except:
                'skip file'

    allInfo = zip(tarTimes,tars,tarSizes)
    tarsInfo =  [[tar,timeFile,size] for timeFile,tar,size in sorted(allInfo,reverse=True)] # name, timeFile, size
    for i in range(len(tarsInfo)):
        file = tarsInfo[i][0]
        size = tarsInfo[i][2]
        print '{:.2f} MB, {}'.format(size / float(10 ** 6), file)
    if len(tars) > 0:
        latestTar = tarsInfo[0]
        latestTime = latestTar[1]
    else:
        latestTar = None
        latestTime = datetime.datetime.strptime('2000-1-1.0.0.0', format(timeFormat))
    # Add igcs to tar file
    print "Compressing igc files"
    tarName = 'igcs{}-backto-{}.tar.gz'.format(nowStr, latestTime.strftime(timeFormat))
    tarPath = '{}/{}'.format(dbBUdir,tarName)
    igcsTar = tarfile.open(tarPath, mode='w:gz')
    igcs = os.listdir(igcsInDir)
    for igc in igcs:
        igcStoredTime = datetime.datetime.fromtimestamp(os.path.getctime('{}/{}'.format(igcsInDir,igc)))
        if igcStoredTime > latestTime:
            try:
                igcsTar.add('{}/{}'.format(igcsInDir,igc))
            except:
                print 'Error adding {} to tar file'.format(igc)
    igcsTar.close()
    size = os.path.getsize(tarPath)
    print 'Saved {:.2f} MB, {}'.format(size / float(10 ** 6), tarName)
    stderr = None
    try:
        ftp.put(tarPath, '{}/{}'.format(igcsOutDir,tarName))  #put requires file name in destination
    except paramiko.SSHException, e:
        print 'Error copying igc tar file to remote archive',e
    sys.exit('stop while testing')

    print
    os.system('sudo ufw allow 4200')
    t.sleep(5)


