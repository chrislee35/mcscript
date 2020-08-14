#!/usr/bin/env python
from mcscript import Client
import os, json
from pprint import pprint

class WarpClient(Client):
    DEFAULT_COMMAND_CALLBACKS = [
        {
            'trigger': 'home',
            'callback': 'self.home',
            'mutual': 'last_only',
        },
        {
            'trigger': 'start',
            'callback': 'self.start',
            'mutual': 'last_only',
        },
        {
            'trigger': 'remember',
            'callback': 'self.remember',
            'mutual': 'last_only',
        },
        {
            'trigger': 'forget',
            'callback': 'self.forget',
            'mutual': 'last_only',
        },
        {
            'trigger': 'goto',
            'callback': 'self.goto',
            'mutual': 'last_only',
        },
        {
            'trigger': 'listpoints',
            'callback': 'self.listpoints',
            'mutual': 'last_only',
        },
    ]
    
    def on_connect(self):
        self.warp_points = {}
        # load previous save points
        if os.path.exists('warp_points.json'):
            with open('warp_points.json', 'r') as fh:
                self.warp_points = json.load(fh)
    
    def home(self, user, trigger, args):
        """!home takes you to your spawn point"""
        userinfo = self.get_user_info(user)
        res = userinfo['data']['response']
        self.teleport(user, {'x': res['SpawnX'], 'y': res['SpawnY'], 'z': res['SpawnZ']})
        
    def start(self, user, trigger, args):
        """!start takes you to the common area"""
        if self.warp_points.get('start'):
            self.teleport(user, self.warp_points['start'])
        else:
            self.msg(user, 'This world has so common area yet.')
        
    def goto(self, user, trigger, args):
        """!goto <pointname>    Warp to a given point."""
        if '.' in args:
            self.msg(user, 'No periods in warp point names.')
        elif self.warp_points.get('%s.%s' % (user, args)):
            self.teleport(user, self.warp_points['%s.%s' % (user, args)])
        elif self.warp_points.get(args):
            self.teleport(user, self.warp_points[args])
        else:
            self.msg(user, 'No point saved by the name of '+args)
            
    def remember(self, user, trigger, args):
        """!remember <pointname> [public]    Remember your current location with a given warp point name.  Add public if you want others to use it"""
        if not args and len(args) > 0:
            self.msg(user, 'pointname is a required argument to !remember.  try !help remember')
            return
            
        if '.' in args:
            self.msg(user, 'No periods in warp point names.')
            return
        pointname, visibility = self.parse_args(args, ['', 'private'])
        userinfo = self.get_user_info(user)
        x,y,z = self.extract_user_position(userinfo, roundPosition=True)
        key = '%s.%s' % (user, pointname)
        if visibility == 'public':
            key = pointname
        
        if self.warp_points.get(key):
            if self.warp_points[key]['owner'] == user:
                # update the pointname
                self.warp_points[key]['x'] = x
                self.warp_points[key]['y'] = y
                self.warp_points[key]['z'] = z
                self.msg(user, 'Updated warp point, %s' % pointname)
            else:
                self.msg(user, 'You cannot update the warp point owned by another player.')
        else:
            self.warp_points[key] = {
                'owner': user,
                'x': x, 'y': y, 'z': z
            }
            self.msg(user, 'Saved warp point, %s' % pointname)
        
        with open('warp_points.json', 'w') as fh:
            json.dump(self.warp_points, fh)
        
    def forget(self, user, trigger, args):
        """!forget <pointname>    Remove a warp point"""
        if '.' in args:
            self.msg(user, 'No periods in warp point names.')
        elif self.warp_points.get('%s.%s' % (user, args)):
            self.warp_points.pop('%s.%s' % (user, args))
            self.msg(user, 'Removed warp point, %s' % args)
        elif self.warp_points.get(args):
            if self.warp_points[args]['owner'] == user:
                self.warp_points.pop(args)
                self.msg(user, 'Removed warp point, %s' % args)
            else:
                self.msg(user, 'You cannot remove the warp point owned by another player.')
        else:
            self.msg(user, 'No point saved by the name of '+args)
            
            
    def listpoints(self, user, tigger, args):
        public = []
        private = []
        for wp in self.warp_points.keys():
            owner = self.warp_points[wp]['owner'] == user
            if '.' in wp:
                if owner:
                    private.append(wp.split('.',1)[1])
            else:
                if owner:
                    public.append('*'+wp)
                else:
                    public.append(wp)
        msg = "Public: [{public}] Private: [{private}]".format(public=', '.join(public), private=', '.join(private))
        self.msg(user, msg)
        
if __name__ == "__main__":
    tc = WarpClient()
    tc.connect("localhost", 55115)