

sudo sudo -u postgres psql -d skylines -c "DELETE FROM igc_files WHERE date_condor='2020-1-5';"
sudo sudo -u postgres psql -d skylines -c "DELETE FROM flights WHERE date_local='2020-1-5';"
sudo sudo -u postgres psql -d skylines -c "DELETE FROM users WHERE last_name='1';"
sudo sudo -u postgres psql -d skylines -c "DELETE FROM clubs WHERE name='group1';"
