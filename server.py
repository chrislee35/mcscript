#!/usr/bin/env python

from mcscript import MCLauncher, MCScriptClientRequestHandler, MCScriptServer
import threading

mc_launch_command = 'jre1.8.0_251/bin/java -Xmx1024M -Xms1024M -jar minecraft_server.1.16.1.jar nogui'
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
