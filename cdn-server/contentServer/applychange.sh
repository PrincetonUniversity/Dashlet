# apply the change of nginx.conf file
sudo cp nginx.conf /usr/local/nginx/conf/
sudo /usr/local/nginx/sbin/nginx -t
sudo /usr/local/nginx/sbin/nginx -s reload
