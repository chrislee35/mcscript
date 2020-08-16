#!/usr/bin/env python
import socket, json, re, struct, math, time, sys
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
        self.commands.append( { 'trigger': trigger, 'mutual': mutual, 'help': callback.__doc__ } )
        self.callbacks[trigger] = callback
        
    def register(self):
        if not self.sock:
            return False
        rep = self.send_request({'type': 'register', 'commands': self.commands})
        if rep['status'] == 'error':
            self.last_error = rep['error']
            return False
        return True
        
    def send_cmd(self, cmd, no_wait=False):
        request = { 'type': 'command', 'cmd': cmd, 'no_wait': no_wait }
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
        
    def fill(self, coord1, coord2, block, oldBlockHandling='replace'):
        x1,y1,z1 = coord1
        x2,y2,z2 = coord2
        vol = sum([ abs(coord1[i]-coord2[i]+1) for i in range(len(coord1))])
        if vol >= 32768:
            # find the greatest dimension, cut it in half and do two fill commands
            cut = 0
            max_d = 0
            for i in range(len(coord1)):
                if abs(coord1[i]-coord2[i]+1) > max_d:
                    max_d = abs(coord1[i]-coord2[i]+1)
                    cut = i
            mid = int((coord1[cut] - coord2[cut])/2)
            midcoord2 = coord2.copy()
            midcoord2[cut] = mid
            midcoord1 = coord1.copy()
            midcoord1[cut] = mid
            self.fill(coord1, midcoord2, block, oldBlockHandling)
            self.fill(midcoord1, coord2, block, oldBlockHandling)
        else:
            cmd = '/fill {x1} {y1} {z1} {x2} {y2} {z2} {block} {handling}'.format(
                x1 = x1, y1 = y1, z1 = z1,
                x2 = x2, y2 = y2, z2 = z2,
                block = block,
                handling = oldBlockHandling
            )
            return self.send_cmd(cmd)
        
    def summon(self, x, y, z, mob, **kwargs):
        cmd = '/summon {mob} {x} {y} {z}'.format(x=x, y=y, z=z, mob=mob)
        if len(kwargs.keys()) > 0:
            opts = ', '.join(['%s:%s' % (x,kwargs[x]) for x in kwargs.keys()])
            cmd += ' {'+opts+'}'
        return self.send_cmd(cmd)
        
    def locate(self, user, target):
        cmd = '/execute as {user} run locate {target}'.format(user=user, target=target)
        resp = self.send_cmd(cmd)
        matches = re.search('\[([\-\d\.]+), ([\-\d\.~]+), ([\-\d\.]+)\]', resp['data']['response'])
        if not matches:
            return None
        nearest = [int(matches.group(1)), matches.group(2), int(matches.group(3))]
        return nearest
        
    def teleport(self, user, coords):
        cmd = '/teleport {user} {x} {y} {z}'.format(user=user, x=coords['x'], y=coords['y'], z=coords['z'])
        resp = self.send_cmd(cmd)
        print(resp)
        return True
        
    def msg(self, user, message):
        cmd = '/msg {user} {message}'.format(user=user, message=message)
        return self.send_cmd(cmd, True)
        
    def grant_advancement(self, user, advancement, method='only', **criterion):
        cmd = '/advancement grant {user} {method} {advancement}'.format(user=user, method=method, advancement=advancement)
        return self.send_cmd(cmd)
        
    def revoke_advancement(self, user, advancement, method='only', **criterion):
        cmd = '/advancement revoke {user} {method} {advancement}'.format(user=user, method=method, advancement=advancement)
        return self.send_cmd(cmd)
        
    def ban_user(self, user, reason=None):
        cmd = '/ban {user}'.format(user=user)
        if reason:
            cmd += ' [{reason}]'.format(reason=reason)
        return self.send_cmd(cmd)
        
    def unban_user(self, user):
        cmd = '/pardon {user}'.format(user=user)
        return self.send_cmd(cmd)
        
    def ban_ip(self, ip, reason=None):
        cmd = '/ban-ip {ip}'.format(ip=ip)
        if reason:
            cmd += ' [{reason}]'.format(reason=reason)
        return self.send_cmd(cmd)

    def unban_ip(self, ip):
        cmd = '/pardon-ip {ip}'.format(ip=ip)
        return self.send_cmd(cmd)
        
    def extract_user_position(self, userinfo, roundPosition=False):
        pos = userinfo['data']['response']['Pos']
        if roundPosition:
            pos = [int(round(x)) for x in pos]
        return pos
        
    def parse_args(self, args, defaults=None):
        if not defaults and not args:
            return None
        if not defaults and len(args) == 0:
            return None
            
        d = defaults
        if not args or len(args) == 0:
            return d

        a = args.split(' ')
        if not defaults:
            return a

        for i in range(len(a)):
            d[i] = type(d[i])(a[i])
        
        return d
        
    def send_request(self, data, get_reply=True):
        jdata = json.dumps(data).encode('UTF-8')
        self.sock.sendall(struct.pack('I', len(jdata))+jdata)
        if get_reply:
            reply = self.get_message()
            return reply
        return None
        
    def connect(self, server_ip, server_port):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.settimeout(None) # blocking io
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
        print(blen)
        l = struct.unpack('I', blen)[0]
        print("len is %d" % l)
        if sys.version_info.major == 3:
            buf = b''
        else:
            buf = ''
        while len(buf) < l:
            buf += self.sock.recv(l-len(buf))
        data = json.loads(buf)
        pprint(data)
        return data
        
    def server_structures(self):
        request = { 'type': 'list_structures' }
        reply = self.send_request(request)
        return [x.replace('minecraft:', '') for x in reply['data']['structures']]
        
    def on_connect(self):
        pass
        
    def before_disconnect(self):
        pass
        
    def _register_command(self, func, trigger, mutual):
        self.add_command(trigger, func, mutual)
        return func
        
    _register_command = staticmethod( _register_command )
    
    def highlight_path(self, start_coords, angle, count, spacing, particle='flash'):
        dx = spacing*math.cos(angle*math.pi/180)
        dz = spacing*math.sin(angle*math.pi/180)
        for i in range(1,count+1):
            cmd = "/execute at @a anchored eyes run particle {particle} ^{dx} ^ ^{dz}".format(dx=dx*i, dz=dz*i, particle=particle)
            self.send_cmd(cmd)
            time.sleep(0.3)

    def distance_and_bearing(self, coords1, coords2):
        x1, y1, z1 = coords1
        x2, y2, z2 = coords2
        
        dx = x2 - x1
        dz = z2 - z1
        
        distance = math.sqrt((dx**2)+(dz**2))
        if dz == 0:
            if dx > 0:
                angle = 0 # due East 
            else:
                angle = 180 # due West
        elif dx == 0:
            if dz > 0:
                angle = -90 # due South
            else:
                angle = 90 # due North
        else:
            angle = math.atan(float(-dz)/dx)*180/math.pi
            
        # convert angle into compass directions
        if angle < 0:
            angle += 360
        
        bearings = ['E', 'ENE', 'NE', 'NNE', 'N', 'NNW', 'NW', 'WNW', 'W', 'WSW', 'SW', 'SSW', 'S', 'SSE', 'SE', 'ESE']
        sextant = int(angle / (360.0/len(bearings)))

        shifted_angle = angle + (180.0/len(bearings))
        bearing = bearings[sextant]
        
        return (distance, angle, bearing)