#!/usr/bin/env python

from mcscript import MCLauncher, MCScriptClientRequestHandler, MCScriptServer
import threading, sys, os

java_bin = '/usr/bin/java'
server_jar = 'server.jar'

if os.environ.get('JAVA_BIN'):
    java_bin = os.environ['JAVA_BIN']
if os.environ.get('MCSERVER_JAR'):
    server_jar = os.environ['MCSERVER_JAR']
    
if len(sys.argv) == 3:
    java_bin = sys.argv[1]
    server_bin = sys.argv[2]

mc_launch_command = '{java_bin} -Xmx1024M -Xms1024M -jar {server_jar} nogui'.format(java_bin=java_bin, server_jar=server_jar)
mc = MCLauncher(mc_launch_command)

HOST, PORT = "localhost", 55115
server = MCScriptServer((HOST, PORT), MCScriptClientRequestHandler)

mc.server = server
server.mc = mc

server_thread = threading.Thread(target=server.serve_forever)
server_thread.daemon = True
server_thread.start()

mc_thread = threading.Thread(target=mc.run)
mc_thread.start()
