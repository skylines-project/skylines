mkdir ~/pgadmin
cd ~/pgadmin
pipenv shell

sudo pipenv install <wheel>
chown -R bret:root /var/lib
chown -R bret:root /var/log
# start:
python ~/.lpocal/share/virtualenvs/pgadmin-WsDn56it/lib/python2.7/site-packages/pgadmin4/pgAdmin4.py