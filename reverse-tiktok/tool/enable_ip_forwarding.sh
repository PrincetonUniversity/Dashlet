sudo sysctl -w net.ipv4.ip_forward=1
sudo iptables -F
sudo iptables -t nat -F
sudo iptables -X
sudo iptables -t nat -A PREROUTING -p tcp --dport 9989 -j DNAT --to-destination 100.64.0.2:9989
sudo iptables -t nat -A POSTROUTING -p tcp -d 100.64.0.2 --dport 9989 -j SNAT --to-source 172.29.130.16
