#!/bin/bash

iptables -I INPUT --proto tcp --dport 6969 --source prospector.pickaxehosting.com -j ACCEPT
iptables -I INPUT --proto tcp --dport 2222 --source prospector.pickaxehosting.com -j ACCEPT
iptables -I INPUT --proto tcp --dport 25565 -j ACCEPT

/etc/init.d/iptables save
