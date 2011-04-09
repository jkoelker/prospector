#!/bin/bash

BASEURL=$1

yum install -y java-1.6.0-openjdk

mkdir -p /usr/local/lib/minecraft

wget -q -O /usr/local/lib/minecraft/minecraft_server.jar ${BASEURL}/MineCraftServer/minecraft_server.jar

#chown minecraft:minecraft /home/minecraft/minecraft_server.jar

