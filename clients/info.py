#!/usr/bin/env python
from mcscript import Client
import math

class InfoClient(Client):
    DEFAULT_COMMAND_CALLBACKS = [
        {
            'trigger': 'whereami',
            'callback': 'self.whereami',
            'mutual': 'last_only',
        },
        {
            'trigger': 'locate',
            'callback': 'self.mylocate',
            'mutual': 'last_only',
        },
        {
            'trigger': 'whereis',
            'callback': 'self.whereis',
            'mutual': 'last_only',
        }
    ]
    def whereami(self, user, trigger, args):
        userinfo = self.get_user_info(user)
        x,y,z = self.extract_user_position(userinfo, roundPosition=True)
        self.send_cmd('/msg {user} You are at [x={x}, y={y}, z={z}]'.format(user=user, x=x, y=y, z=z))
        
    def mylocate(self, user, trigger, args):
        if args and len(args) > 0:
            target_coords = self.locate(user, args)
            if not target_coords:
                self.msg(user, 'cannot find %s' % args)
                return
            userinfo = self.get_user_info(user)
            player_coords = self.extract_user_position(userinfo)
            distance, angle, bearing = self.distance_and_bearing(player_coords, target_coords)
            distance = int(distance)
            if distance > 100:
                self.highlight_path( player_coords, angle, 6, 5 )
            self.msg(user, '%s is %s (%d blocks away)' % (args, bearing, distance))
        
    def on_connect(self):
        resp = self.send_cmd('/say info module is online')
    
    def whereis(self, user, trigger, args):
        if args and len(args) > 0:
            if args == user:
                self.send_cmd('/msg {user} You are where you are.'.format(user))
                return
                
            userinfo1 = self.get_user_info(user)
            x1,y1,z1 = self.extract_user_position(userinfo1)
            userinfo2 = self.get_user_info(args)
            x2,y2,z2 = self.extract_user_position(userinfo2)
            
            distance, angle, bearing = self.distance_and_bearing((x1,y1,z2), (x2,y2,z2))
            distance = int(distance/30)*30
            self.send_cmd('/msg {user} {args} is approximate {distance} blocks at a bearing of {bearing}'.format(user=user, reply=reply))
            
            if distance > 100:
                self.highlight_path( (x1,y1,z1), angle, 6, 5 )

if __name__ == "__main__":
    tc = InfoClient()
    tc.connect("localhost", 55115)