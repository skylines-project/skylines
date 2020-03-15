sudo apt-get update
sudo apt-get install nginx

sudo apt-get install software-properties-common
sudo add-apt-repository ppa:certbot/certbot
sudo apt-get update
sudo apt-get install certbot

cd /etc/nginx/
sudo cp nginx.conf nginx.conf.orig

sudo cp sites-available/default sites-available/skylinescondor.com
sudo ln -s /etc/nginx/sites-available/skylinescondor.com /etc/nginx/sites-enabled/
sudo rm sites-enabled/default

sudo vim sites-available/skylinescondor.com
# replace;
#    server_name _;
# with 
# server_name skylinescondor.com;

# location ^~ /.well-known/acme-challenge/ {
# 	allow all;
#   default_type "text/plain";
# }
sudo service nginx reload

sudo certbot certonly --webroot --webroot-path=/var/www/html -d skylinescondor.com

The client lacks sufficient authorization :: Invalid response from .well-known/acme-challenge/