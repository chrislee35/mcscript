#!/usr/bin/env python
import socket, json, re, struct
from pprint import pprint

class Client(object):
    DEFAULT_COMMAND_CALLBACKS = []
    
    def __init__(self):
        self.commands = []
        self.callbacks = {}
        self.sock = None
        self.last_error = None
        self.running = False
        for cmd in self.DEFAULT_COMMAND_CALLBACKS:
            self.add_command(cmd['trigger'], eval(cmd['callback']), cmd.get('mutual', 'first_only'))
        
    def add_command(self, trigger, callback, mutual='first_only'):
        if not re.match('[a-z_]+', trigger):
            return False
        self.commands.append( { 'trigger': trigger, 'mutual': mutual } )
        self.callbacks[trigger] = callback
        
    def register(self):
        if not self.sock:
            return False
        rep = self.send_request({'type': 'register', 'commands': self.commands})
        pprint(rep)
        if rep['status'] == 'error':
            self.last_error = rep['error']
            return False
        return True
        
    def send_cmd(self, cmd):
        request = { 'type': 'command', 'cmd': cmd }
        reply = self.send_request(request)
        return reply
        
    def get_user_info(self, user):
        request = { 'type': 'userinfo', 'user': user }
        reply = self.send_request(request)
        return reply
        
    def setblock(self, x, y ,z, block, **kwargs):
        cmd = '/setblock {x} {y} {z} {block}'.format(x=x, y=y, z=z, block=block)
        if len(kwargs.keys()) > 0:
            opts = ','.join(['%s=%s' % (x,kwargs[x]) for x in kwargs.keys()])
            cmd += '['+opts+']'
        return self.send_cmd(cmd)
        
    def summon(self, x, y, z, mob, **kwargs):
        cmd = '/summon {mob} {x} {y} {z}'.format(x=x, y=y, z=z, mob=mob)
        if len(kwargs.keys()) > 0:
            opts = ', '.join(['%s:%s' % (x,kwargs[x]) for x in kwargs.keys()])
            cmd += ' {'+opts+'}'
        return self.send_cmd(cmd)
        
    def extract_user_position(self, userinfo, roundPosition=False):
        pos = userinfo['data']['response']['Pos']
        if roundPosition:
            pos = [int(round(x)) for x in pos]
        return pos
        
    def send_request(self, data, get_reply=True):
        jdata = json.dumps(data)
        self.sock.sendall(struct.pack('I', len(jdata))+jdata)
        if get_reply:
            reply = self.get_message()
            return reply
        return None
        
    def connect(self, server_ip, server_port):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((server_ip, server_port))
        self.running = True
        self.on_connect()
        self.register()
        while self.running:
            data = self.get_message()
            if data['type'] == 'trigger':
                trigger = data['trigger']
                if self.callbacks.get(trigger):
                    self.callbacks[trigger](data['user'], data['trigger'], data.get('args'))
        self.before_disconnect()
        self.sock.close()

    def get_message(self):
        print("reading len")
        blen = self.sock.recv(4)
        l = struct.unpack('I', blen)[0]
        print("len is %d" % l)
        buf = ""
        while len(buf) < l:
            buf += self.sock.recv(l-len(buf))
        data = json.loads(buf)
        pprint(data)
        return data
        
    def on_connect(self):
        pass
        
    def before_disconnect(self):
        pass
        
    def _register_command(self, func, trigger, mutual):
        self.add_command(trigger, fun, mutual)
        return func
        
    _register_command = staticmethod( _register_command )
    