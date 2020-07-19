#!/usr/bin/env python
from mcscript import Client

class TowerClient(Client):
    DEFAULT_COMMAND_CALLBACKS = [{
        'trigger': 'tower',
        'callback': 'self.tower',
        'mutual': 'shared',
    }]
    def tower(self, user, trigger, args):
        userinfo = self.get_user_info(user)
        x,y,z = self.extract_user_position(userinfo, roundPosition=True)
        
        #  E +X
        #N B<B S -> +Z
        #  v@^
        #  B>B
        #  W
        
        for level in range(10):
            i = level * 4
            stair = 'minecraft:smooth_quartz_stairs'
            block = 'minecraft:smooth_quartz'
            self.setblock(x+1, y+i, z, stair, facing='north')
            self.setblock(x+1, y+i, z-1, block)
            self.setblock(x, y+i+1, z-1, stair, facing='west')
            self.setblock(x-1, y+i+1, z-1, block)
            self.setblock(x-1, y+i+2, z, stair, facing='south')
            self.setblock(x-1, y+i+2, z+1, block)
            self.setblock(x, y+i+3, z+1, stair, facing='east')
            self.setblock(x+1, y+i+3, z+1, block)
        
    def on_connect(self):
        resp = self.send_cmd('/say tower module is online')
    
if __name__ == "__main__":
    tc = TowerClient()
    tc.connect("localhost", 55115)