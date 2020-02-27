sudo sudo -u postgres psql -d skylines -c "DELETE FROM igc_files WHERE lower(filename) LIKE '%rex%';"
sudo sudo -u postgres psql -d skylines -c "DELETE FROM flights WHERE competition_id='RS';"
sudo sudo -u postgres psql -d skylines -c "DELETE FROM users WHERE last_name='3';"
