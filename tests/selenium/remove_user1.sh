

sudo sudo -u postgres psql -d skylines -c "DELETE FROM igc_files WHERE date_condor='2019-10-15';"
sudo sudo -u postgres psql -d skylines -c "DELETE FROM flights WHERE date_local='2019-10-25';"
sudo sudo -u postgres psql -d skylines -c "DELETE FROM users WHERE last_name='one';"
sudo sudo -u postgres psql -d skylines -c "DELETE FROM clubs WHERE name='group1';"
