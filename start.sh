#!/usr/bin/env bash

export PYTHONPATH=${PYTHONPATH:=/Volumes/taifun/code/python/minecraft}
export JAVA_BIN=${JAVA_BIN:=/usr/bin/java}
export MCSERVER_JAR=${MCSERVER_JAR:=server.jar}
python3 /Volumes/taifun/code/python/minecraft/server.py

