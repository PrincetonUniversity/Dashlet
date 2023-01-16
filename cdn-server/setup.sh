sudo apt update
sudo apt install build-essential git
sudo apt install libpcre3-dev libssl-dev zlib1g-dev
git clone https://github.com/arut/nginx-rtmp-module.git
git clone https://github.com/nginx/nginx.git
cd nginx
./auto/configure --add-module=../nginx-rtmp-module
make
sudo make install
