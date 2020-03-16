sudo chown -R $USER /var/log/
sudo chown -R $USER /lib/log/
mkdir ~/pgadmin
cd ~/pgadmin
pipenv shell

#now run 'pipenv install <wheel>'
#python ~/.local/share/virtualenvs/pgadmin-WsDn56it/lib/python2.7/site-packages/pgadmin4/pgAdmin4.py