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
            'callback': 'self.locate',
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
        
    def locate(self, user, trigger, args):
        if args and len(args) > 0:
            resp = self.send_cmd('/locate {args}'.format(args=args))
            print(resp)
            reply = resp['data']['response'].split(': ', 1)[1]
            self.send_cmd('/msg {user} {reply}'.format(user=user, reply=reply))
        
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
            
            distance, bearing = self.distance_and_bearing((x1,y1,z2), (x2,y2,z2))
            self.send_cmd('/msg {user} {args} is approximate {distance} blocks at a bearing of {bearing}'.format(user=user, reply=reply))

    def distance_and_bearing(self, coords1, coords2):
        x1, y1, z1 = coords1
        x2, y2, x2 = coords2
        
        dx = x2 - x1
        dz = z2 - z1
        
        distance = int(round(math.sqrt((dx**2)+(dz**2))/30))*30
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

        shifted_angle += 180.0/len(bearings)
        bearing = bearings[sextant]
        
        return (distance, bearing)
        
if __name__ == "__main__":
    tc = InfoClient()
    tc.connect("localhost", 55115)