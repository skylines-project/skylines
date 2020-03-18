mkdir ~/pgadmin
cd ~/pgadmin
pipenv shell

sudo pipenv install <wheel>

# lots of permissioni problems with pgadmin.

https://stackoverflow.com/questions/46707935/oserror-errno-13-permission-denied-var-lib-pgadmin
f you do not want to change the permission of anything, you can always override default paths in pgAdmin4.

Create a file named config_local.py (if not already present) at your installation location ../pgadmin4/web/

import os
DATA_DIR = os.path.realpath(os.path.expanduser(u'~/.pgadmin/'))
LOG_FILE = os.path.join(DATA_DIR, 'pgadmin4.log')
SQLITE_PATH = os.path.join(DATA_DIR, 'pgadmin4.db')
SESSION_DB_PATH = os.path.join(DATA_DIR, 'sessions') 
STORAGE_DIR = os.path.join(DATA_DIR, 'storage')



# start:
python ~/.lpocal/share/virtualenvs/pgadmin-WsDn56it/lib/python2.7/site-packages/pgadmin4/pgAdmin4.pyls

I