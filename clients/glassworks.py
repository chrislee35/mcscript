#!/usr/bin/env python
from mcscript import Client
from random import shuffle, randrange
import math

class GlassClient(Client):
    DEFAULT_COMMAND_CALLBACKS = [
        {
            'trigger': 'dome',
            'callback': 'self.dome',
            'mutual': 'last_only',
        },
        {
            'trigger': 'cyl',
            'callback': 'self.cyl',
            'mutual': 'last_only',
        },
    ]
    def dome(self, user, trigger, args):
        """!dome height wall_block lighting_block floor_block"""
        userinfo = self.get_user_info(user)
        x,y,z = self.extract_user_position(userinfo, roundPosition=True)
        h, walls, lighting, floor = self.parse_args(args, [15, 'minecraft:glass', 'minecraft:sea_lantern', 'minecraft:smooth_quartz'])

        self.disk( (x,y-1,z), h, floor )
        self.setblock(x, y+h, z, lighting)
        for i in range(1, h+1):
            a = (float(i)/h)*math.pi/2
            r = int(round(math.sin(a)*h))
            if i % 5 == 0:
                block = lighting
            else:
                block = walls
            self.circle( (x, y+h-i, z), r, block)
        for i in range(1, h+1)
            self.disk( (x, y+h-i, z), r-1, 'minecraft:air')
            
    def cyl(self, user, trigger, args):
        """!cyl height radius wall_block floor_block"""
        userinfo = self.get_user_info(user)
        x,y,z = self.extract_user_position(userinfo, roundPosition=True)
        h, r, walls, floor = self.parse_args(args, [15, 3, 'minecraft:glass', 'minecraft:smooth_quartz'])
        self.disk( (x,y-1,z), r, floor )
        self.cylinder( (x,y,z), r, h, walls)

    def disk(self, center, r, block, args=None):
        last_x = 0
        last_z = 0
    
        for angle in range(90):
            delta_x = int(r * math.cos(math.pi*angle/180))
            delta_y = 0
            delta_z = int(r * math.sin(math.pi*angle/180))

            if last_x == delta_x and last_z == delta_z:
                continue
            last_x = delta_x
            last_z = delta_z
            for i in range(delta_x):
                for j in range(delta_z):
                    self.send_cmd("/setblock {x} {y} {z} {block}".format(x=center[0]+i, y=center[1]+delta_y, z=center[2]+j, block=block))
                    self.send_cmd("/setblock {x} {y} {z} {block}".format(x=center[0]+i, y=center[1]+delta_y, z=center[2]-j, block=block))
                    self.send_cmd("/setblock {x} {y} {z} {block}".format(x=center[0]-i, y=center[1]+delta_y, z=center[2]+j, block=block))
                    self.send_cmd("/setblock {x} {y} {z} {block}".format(x=center[0]-i, y=center[1]+delta_y, z=center[2]-j, block=block))

    def circle(self, center, r, block):
        last_x = 0
        last_z = 0
    
        for angle in range(90):
            delta_x = int(r * math.cos(math.pi*angle/180))
            delta_y = 0
            delta_z = int(r * math.sin(math.pi*angle/180))

            if last_x == delta_x and last_z == delta_z:
                continue
            last_x = delta_x
            last_z = delta_z
            self.send_cmd("/setblock {x} {y} {z} {block}".format(x=center[0]+delta_x, y=center[1]+delta_y, z=center[2]+delta_z, block=block))
            self.send_cmd("/setblock {x} {y} {z} {block}".format(x=center[0]+delta_x, y=center[1]+delta_y, z=center[2]-delta_z, block=block))
            self.send_cmd("/setblock {x} {y} {z} {block}".format(x=center[0]-delta_x, y=center[1]+delta_y, z=center[2]+delta_z, block=block))
            self.send_cmd("/setblock {x} {y} {z} {block}".format(x=center[0]-delta_x, y=center[1]+delta_y, z=center[2]-delta_z, block=block))
    
    def cylinder(self, center, r, h, block):
        for i in range(h):
            self.circle((center[0], center[1]+i, center[2]), r, block)
            
if __name__ == "__main__":
    tc = GlassClient()
    tc.connect("localhost", 55115)