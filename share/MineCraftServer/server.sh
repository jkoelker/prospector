#!/bin/bash

BASEURL=$1

yum install -y java-1.6.0-openjdk

wget -q -O /home/minecraft/minecraft_server.jar ${BASEURL}/MineCraftServer/minecraft_server.jar

chown minecraft:minecraft /home/minecraft/minecraft_server.jar

