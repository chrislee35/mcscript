#!/usr/bin/env python
from mcscript import Client
import nbtlib, os

class NBTClient(Client):
    DEFAULT_COMMAND_CALLBACKS = [
        {
            'trigger': 'nbt',
            'callback': 'self.nbt_load',
            'mutual': 'last_only',
        },
    ]
    def nbt_load(self, user, trigger, args):
        userinfo = self.get_user_info(user)
        x,y,z = self.extract_user_position(userinfo, roundPosition=True)
        
        if args and len(args) > 0:
            filename = 'nbt/{args}.nbt'.format(args=args)
            if os.path.exists(filename):
                nbt = nbtlib.load(filename)
                palette = nbt.get(nbt.root_name).get('palette')
                blocks = nbt.get(nbt.root_name).get('blocks')
                author = nbt.get(nbt.root_name).get('author')

                for block in blocks:
                    dx,dy,dz = [ int(x) for x in block['pos'] ]
                    state = int(block['state'])
                    pal = palette[state]
                    pal_name = pal['Name']
                    pal_props = {}
                    
                    for p in pal.get('Properties', []):
                        pal_props[str(p)] = str(pal['Properties'][p])
                    
                    print(pal_name)
                    print(pal_props)
                    if pal_name == 'minecraft:log' or pal_name == 'minecraft:log2':
                        pal_name = 'minecraft:{variant}_log'.format(variant=pal_props.pop('variant'))
                    elif pal_name == 'minecraft:planks':
                        pal_name = 'minecraft:{variant}_plank'.format(variant=pal_props.pop('variant'))
                    print(pal_name)
                    print(pal_props)
                        
                    self.setblock(x+dx, y+dy, z+dz, pal_name, **pal_props)
            else:
                self.msg(user, "Could not find {args}.nbt".format(args=args))
    

if __name__ == "__main__":
    tc = NBTClient()
    tc.connect("localhost", 55115)
