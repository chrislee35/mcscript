#!/usr/bin/env python
import sys, json, time, struct, re, subprocess, os, glob
import threading
import traceback

try:
    import SocketServer
except ModuleNotFoundError:
    import socketserver as SocketServer
    
from subprocess import Popen, PIPE
import shlex
from pprint import pprint
from mcscript import MCUtils

class MCScriptClientRequestHandler(SocketServer.BaseRequestHandler):
    DEBUG = True
    client_num = 1
    
    def handle(self):
        self.client_id = MCScriptClientRequestHandler.client_num
        MCScriptClientRequestHandler.client_num += 1
        running = True
        try:
            while running:
                request = self.get_message()
                self.process_request(request)
        except Exception as e:
            track = traceback.format_exc()
            running = False
            print(track)
        finally:
            self.deregister()
            
    def debug(self, message):
        if self.DEBUG:
            print("CID%d: %s" % (self.client_id, message))
            
    def deregister(self):
        self.server.registration_lock.acquire()
        self.debug("deregistering client")
        cmds = self.server.cmds
        keys = cmds.keys()
        to_remove = []
        for trigger in keys:
            cmd = cmds[trigger]
            if self in cmd['clients']:
                cmd['clients'].remove(self)
            if len(cmd['clients']) == 0:
                to_remove.append(trigger)
                
        for trigger in to_remove:
            cmds.pop(trigger)
        self.server.registration_lock.release()
                
    def get_message(self):
        self.debug("reading len")
        blen = self.request.recv(4)
        l = struct.unpack('I', blen)[0]
        self.debug("length = %d" % l)
        if sys.version_info.major == 3:
            buf = b''
        else:
            buf = ''
        while len(buf) < l:
            buf += self.request.recv(l-len(buf))
        data = json.loads(buf)
        self.debug(data)
        return data
            
    def process_request(self, request):
        t = request.get('type')
        if not t:
            # invalid request
            self.send_error('request type unspecified')
        elif t == 'register':
            self.debug("processing registration")
            self.process_registration(request)
        elif t == 'command':
            self.debug("processing command")
            response = self.server.mc.exec_command(request['cmd'])
            self.send_success({'type': 'command_response', 'response': response})
        elif t == 'list_structures':
            self.debug("processing list_structures request")
            structures = [":".join(x.replace("world/generated/","").replace("/structures/", "/").replace('.nbt','').split('/')) for x in glob.glob("world/generated/*/structures/*.nbt")]
            self.send_success({'type': 'list_structures_response', 'structures': structures})
        elif t == 'userinfo':
            self.debug("processing userinfo")
            response = self.server.mc.get_user_information(request['user'])
            self.send_success({'type': 'userinfo_response', 'response': response})
        else:
            # invalid request
            self.send_error('request type unknown: %s' % request['type'])
            
    def process_registration(self, request):
        if not request.get('commands'):
            self.send_error('could not find commands for registration')
        else:
            registrations = {}
            for cmd in request['commands']:
                if not cmd.get('trigger'):
                    self.send_error('no trigger field in command')
                    return
                elif not re.match('[a-z_]+', cmd['trigger']):
                    self.send_error('trigger must be all lowercase a-z and underscores')
                    return
                elif not cmd.get('mutual'):
                    self.send_error('no mutual field in command')
                    return
                elif not cmd['mutual'] in ['shared', 'first_only', 'last_only']:
                    self.send_error('invalid value for mutual field in command: %s' % cmd['mutual'])
                    return
                elif self.server.cmds.get(cmd['trigger']):
                    # there's already a registered client for this trigger
                    registration = self.server.cmds[cmd['trigger']]
                    if registration['mutual'] == 'first_only' and registration['clients'] != [self]:
                        self.send_error('cmd %s is already owned exclusively by another client' % cmd['trigger'])
                        return
                    elif registration['mutual'] == 'shared' and cmd['mutual'] != 'shared':
                        self.send_error('cmd %s is already registered as shared and you tried to claim it exclusively' % cmd['trigger'])
                        return
                    else:
                        registrations[cmd['trigger']] = { 'mutual': cmd['mutual'], 'clients': [self] }
                        if cmd.get('help'):
                            registrations[cmd['trigger']]['help'] = cmd['help']
                else:
                    registrations[cmd['trigger']] = { 'mutual': cmd['mutual'], 'clients': [self] }
                    if cmd.get('help'):
                        registrations[cmd['trigger']]['help'] = cmd['help']
            
            self.server.registration_lock.acquire()
            for trigger in registrations:
                if self.server.cmds.get(trigger):
                    if self.server.cmds[trigger]['mutual'] == 'shared':
                        self.server.cmds[trigger]['clients'].append(self)
                    elif self.server.cmds[trigger]['mutual'] == 'last_only':
                        self.server.cmds[trigger]['clients'] = [self]
                else:
                    self.server.cmds[trigger] = registrations[trigger]
                    
                if registrations[trigger].get('help'):
                    self.server.cmds[trigger]['help'] = registrations[trigger]['help']
            self.server.registration_lock.release()
            
            self.send_success({'message': '%d commands registered' % len(registrations.keys())})
            #pprint(self.server.cmds)
        
    def execute_cmd(self, request):
        if request.get('no_reply'):
            self.server.mc.exec_command(request['cmd'], True)
            self.send_success(None)
        else:
            response = self.server.mc.exec_command(request['cmd'])
            self.send_success({'response': response})
        
    def send_trigger(self, user, trigger, args=None):
        request = {
            'type': 'trigger',
            'user': user,
            'trigger': trigger,
        }
        if args:
            request['args'] = args
        self.send_payload(json.dumps(request))

    def send_payload(self, payload):
        if sys.version_info.major == 3:
            payload = payload.encode('UTF-8')
        self.request.sendall(struct.pack('I', len(payload))+payload)
        
    def send_success(self, data=None):
        self.send_payload(self.json_success(data))
        
    def send_error(self, error):
        self.debug(error)
        self.send_payload(self.json_error(error))
        
    def json_success(self, data=None):
        if data:
            return json.dumps({'status': 'ok', 'data': data})
        else:
            return json.dumps({'status': 'ok'})

    def json_error(self, error):
        return json.dumps({'status':'error', 'error': error})
        
class MCScriptServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
    def __init__(self, host_port, request_handler):
        SocketServer.TCPServer.__init__(self, host_port, request_handler)
        self.mc = None
        self.clients = {}
        self.cmds = {}
        self.registration_lock = threading.Lock()
        
    def msg(self, user, message):
        self.mc.exec_command("/msg {user} {message}".format(user=user, message=message), True)
        
    def process_trigger(self, user, trigger, args=None):
        if trigger == "help":
            if not args:
                self.msg(user, "available triggers: {cmds}".format(cmds=" ".join(self.cmds.keys())))
            else:
                if not self.cmds.get(args):
                    self.msg(user, "unknown trigger: {args}".format(args=args))
                else:
                    h = self.cmds[args].get('help')
                    if not h:
                        self.msg(user, "{args} has no help".format(user=user, args=args))
                    else:
                        self.msg(user, h)
        elif not self.cmds.get(trigger):
            self.msg(user, "unknown trigger: {trigger}".format(trigger=trigger))
        else:
            for client in self.cmds[trigger]['clients']:
                try:
                    client.send_trigger(user, trigger, args)
                except Exception:
                    client.deregister()

class MCLauncher:
    DEBUG = True
    RE_PLAYER_CMD=re.compile('<([^>]+)> \!([a-z_]+)(.*)\n')
    def __init__(self, mc_launch_command):
        self.mc_launch_command = mc_launch_command
        self.mc_proc = None
        self.mc_in = None
        self.mc_out = None
        self.server = None
        self.running = False
        self.buffer = []
        self.max_buffer = 100
        
        # these locks allow clients to submit commands and await the answer
        self.cmd_lock = threading.Lock()
        self.ans_lock = threading.Lock()
        
    def launch_minecraft(self):
        args = shlex.split(self.mc_launch_command)
        bufsize = 1 # line buffered
        self.debug('starting MC: %s' % self.mc_launch_command)
        p = subprocess.Popen(args, bufsize=bufsize, stdin=PIPE, stdout=PIPE, close_fds=True)
        self.mc_proc = p
        self.mc_out = p.stdout
        self.mc_in = p.stdin
        
    def debug(self, message):
        if self.DEBUG:
            print(message)
    
    def wait_for_command(self):
        while self.running:
            line = self.mc_out.readline()
            if type(line) == bytes:
                line = line.decode('UTF-8')
            elif type(line) == unicode:
                line = str(line)
                
            if line == '':
                continue
            elif line == None:
                self.running = False
                return
                
            print(line.strip())

            if len(self.buffer) > self.max_buffer:
                self.buffer.pop(0)
            self.buffer.append(line)
            
            # this is for player-initiated actions
            if self.RE_PLAYER_CMD.search(line):
                match = self.RE_PLAYER_CMD.search(line)
                user = match.group(1)
                cmd = match.group(2).strip()
                args = match.group(3)
                if args and len(args) > 0:
                    args = args.strip()
                self.server.process_trigger(user, cmd, args)
            else:
                # if a thread is waiting on an answer
                if self.ans_lock.locked():
                    self.debug("there's a thread awaiting an answer")
                    # put the line in the answer slot
                    self.answer = line
                    # release the answer lock
                    self.ans_lock.release()
        
    def exec_command(self, cmd, no_reply=False):
        # acquire the cmd and answer locks
        self.debug("executing cmd: {cmd}".format(cmd=cmd))
        self.debug("acquiring both locks")
        self.cmd_lock.acquire()
        #print("acquiring answer lock")
        self.ans_lock.acquire()
        # submit the cmd
        #print("writing cmd: %s" % cmd)
        if sys.version_info.major == 3:
            self.mc_in.write(cmd.encode('UTF-8')+b'\n')
        else:
            self.mc_in.write(cmd+'\n')
        self.mc_in.flush()
        # wait for the answer lock to unlock (by the wait_for_command block)
        if no_reply:
            ans = None
        else:
            self.debug("waiting for answer lock")
            self.ans_lock.acquire()
            # get the answer
            ans = self.answer
            self.debug("got answer: %s" % ans)
        # release both locks
        self.debug("releasing both locks")
        if self.ans_lock.locked():
            self.ans_lock.release()
        self.cmd_lock.release()
        return ans
        
    def get_user_information(self, user):
        info = self.exec_command('/data get entity {user}'.format(user=user))
        info = info[info.find('{'):]
        info = re.sub('UUID: \[(\w+);', 'UUID: ["\\1",', info)
        data = MCUtils.convertMinecraftJson(info)
        return data
        
    def run(self):
        if not self.mc_proc:
            self.launch_minecraft()
        self.running = True
        while self.running:
            self.wait_for_command()
    
