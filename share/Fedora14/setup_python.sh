#!/bin/bash

yum groupinstall -y "Development Libraries" "Development Tools" &&
yum install -y python-setuptools openssl-devel &&
easy_install -U pip &&
pip install fabric &&
pip install twisted &&
pip install pyasn1
