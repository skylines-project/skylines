#create backup
sudo -u bret pg_dump --format=custom skylines > /home/bret/servers/database-backups/skylinesdump.custom

#copy to U18-Nginx server
scp /home/bret/servers/database-backups/skylinesdump.custom bret@192.168.1.241:/home/bret/google_drive

scp -r /home/bret/servers/repo-skylinesC/skylinesC/htdocs/files/*.igc bret@192.168.1.241:/home/bret/google_drive/htdocs/files