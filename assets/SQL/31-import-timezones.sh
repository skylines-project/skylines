curl -O http://efele.net/maps/tz/world/tz_world.zip
unzip tz_world.zip
rm tz_world.zip
cd world
shp2pgsql -D tz_world.shp > dump.sql
psql skylines -f dump.sql
cd ..
rm -r world
