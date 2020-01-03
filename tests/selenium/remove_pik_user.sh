

sudo sudo -u postgres psql -d skylines -c "DELETE FROM igc_files WHERE date_condor='2019-03-12';"
sudo sudo -u postgres psql -d skylines -c "DELETE FROM flights WHERE date_local='2019-03-12';"
sudo sudo -u postgres psql -d skylines -c "DELETE FROM users WHERE first_name='pik';"
sudo sudo -u postgres psql -d skylines -c "DELETE FROM clubs WHERE name='newgroup';"