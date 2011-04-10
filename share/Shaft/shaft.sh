#!/bin/bash

BASEURL=$1

mkdir -m 700 -p /root/.ssh

echo "Host *" >> /root/.ssh/config
echo "CheckHostIP no" >> /root/.ssh/config
echo "StrictHostKeyChecking no" >> /root/.ssh/config
echo "GSSAPIAuthentication no" >> /root/.ssh/config
echo "ServerAliveInterval 5" >> /root/.ssh/config

wget -q -O /root/.ssh/id_rsa ${BASEURL}/Shaft/id_rsa
wget -q -O /root/.ssh/id_rsa.pub ${BASEURL}/Shaft/id_rsa.pub

chmod 0600 /root/.ssh/id_rsa

pip-python install git+ssh://git@github.com/jkoelker/shaft.git

chmod 0755 /etc/init.d/shaft
chkconfig shaft on
/etc/init.d/shaft start

