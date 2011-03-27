#!/bin/bash

BASEURL=$1

mkdir -m 700 -p /root/.ssh

wget -q -O /root/.ssh/id_rsa ${BASEURL}/Shaft/id_rsa
wget -q -O /root/.ssh/id_rsa.pub ${BASEURL}/Shaft/id_rsa.pub

chmod 0600 /root/.ssh/id_rsa

pip-python install git+ssh://git@github.com/jkoelker/shaft.git

chmod 0755 /etc/init.d/shaft
chkconfig shaft on
/etc/init.d/shaft start

