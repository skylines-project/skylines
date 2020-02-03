

sudo sudo -u postgres psql -d skylines -c "DELETE FROM igc_files WHERE date_condor='2020-1-7';"
sudo sudo -u postgres psql -d skylines -c "DELETE FROM flights WHERE date_local='2020-1-7';"
sudo sudo -u postgres psql -d skylines -c "DELETE FROM users WHERE last_name='2';"
sudo sudo -u postgres psql -d skylines -c "DELETE FROM clubs WHERE name='group2';"
