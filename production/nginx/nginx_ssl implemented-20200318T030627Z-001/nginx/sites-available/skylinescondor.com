server {
	    listen 80 default_server;
	    listen [::]:80 default_server;
	    server_name skylinescondor.com;

	    return 301 https://$server_name$request_uri;
	}
 
server {

	    # SSL configuration
	    listen 443 ssl default_server;
	    listen [::]:443 ssl default_server;

	    include snippets/ssl-skylinescondor.com.conf;
	    include snippets/ssl-params.conf;
	}

