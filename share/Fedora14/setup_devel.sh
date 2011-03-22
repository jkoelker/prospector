#!/bin/bash

yum groupinstall -y "Development Libraries" "Development Tools" &&
yum install -y python-setuptools openssl-devel

