mkdir ~/pgadmin
cd ~/pgadmin
pipenv shell

sudo pipenv install <wheel>

# Permissioni problems with pgadmin.

#https://stackoverflow.com/questions/46707935/oserror-errno-13-permission-denied-var-lib-pgadmin
vim ~/.local/share/virtualenvs/pgadmin-WsDn56it/lib/python2.7/site-packages/pgadmin4/config_local.py
#paste
import os 
DATA_DIR = os.path.realpath(os.path.expanduser(u'~/.pgadmin/')) 
LOG_FILE = os.path.join(DATA_DIR, 'pgadmin4.log') 
SQLITE_PATH = os.path.join(DATA_DIR, 'pgadmin4.db') 
SESSION_DB_PATH = os.path.join(DATA_DIR, 'sessions') 
STORAGE_DIR = os.path.join(DATA_DIR, 'storage')

!!!This solves the var/lib permission problem. 



# start:
python ~/.local/share/virtualenvs/pgadmin-WsDn56it/lib/python2.7/site-packages/pgadmin4/pgAdmin4.py

make sure password is set:  psql skylines <then> ALTER USER bret PASSWORD '<password>';
