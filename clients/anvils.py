#!/usr/bin/env python
from mcscript import Client
import time
import math

class HazardClient(Client):
    DEFAULT_COMMAND_CALLBACKS = [
        {
            'trigger': 'anvils',
            'callback': 'self.anvils',
            'mutual': 'last_only',
        },
        {
            'trigger': 'stop',
            'callback': 'self.stop_anvils',
            'mutual': 'last_only',
        },
        {
            'trigger': 'creeperz',
            'callback': 'self.creeperz',
            'mutual': 'last_only',
        }
    ]
    def anvils(self, user, trigger, args):
        
        self.anvils = True
        for i in range(6):
            if not self.running:
                break
            userinfo = self.get_user_info(user)
            x,y,z = self.extract_user_position(userinfo, roundPosition=True)
            self.setblock(x, y+20, z, "minecraft:chipped_anvil")
            time.sleep(5)
        
    def stop_anvils(self, user, trigger, args):
        self.anvils = False
        
    def on_connect(self):
        self.anvils = False
        resp = self.send_cmd('/say hazard module is online')
    
    def creeperz(self, user, trigger, args):
        
        if user == 'ahoyasan' and args and len(args) > 0:
            userinfo = self.get_user_info(args)
            x,y,z = self.extract_user_position(userinfo, roundPosition=True)
            r = 10
            last_x = last_z = 0
            for angle in range(360):
                delta_x = int(r * math.cos(math.pi*angle/180))
                delta_z = int(r * math.sin(math.pi*angle/180))

                if last_x == delta_x and last_z == delta_z:
                    continue
                last_x = delta_x
                last_z = delta_z
                
                self.summon(x+delta_x, y, z+delta_z, 'minecraft:creeper', powered=1)

if __name__ == "__main__":
    tc = HazardClient()
    tc.connect("localhost", 55115)