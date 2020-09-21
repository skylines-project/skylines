unlink /etc/nginx/sites-enabled/skylinescondor.com
ln -s /etc/nginx/sites-available/acme-challenge /etc/nginx/sites-enabled
systemctl restart nginx
certbot renew # remove --dry run part after testing
unlink /etc/nginx/sites-enabled/acme-challenge
ln -s /etc/nginx/sites-available/skylinescondor.com /etc/nginx/sites-enabled
systemctl restart nginx