#!/usr/bin/env python
from mcscript import Client
#import nbtlib
import os, json

class StructuresClient(Client):
    DEFAULT_COMMAND_CALLBACKS = [
        # {
        #     'trigger': 'nbt',
        #     'callback': 'self.nbt_load',
        #     'mutual': 'last_only',
        # },
        {
            'trigger': 'build',
            'callback': 'self.build',
            'mutual': 'last_only'
        },
        {
            'trigger': 'buildplan',
            'callback': 'self.buildplan',
            'mutual': 'last_only'
        },
        {
            'trigger': 'capture',
            'callback': 'self.captureplan',
            'mutual': 'last_only'
        },
    ]
    
    def on_connect(self):
        if os.path.exists('plans.json'):
            with open('plans.json', 'r') as fh:
                self.plans = json.load(fh)
        else:
            self.plans = {
                'largetown1': [
                    {
                        'structure': 'town1',
                        'rotation': 'NONE',
                        'mirror': 'NONE',
                        'dx': -32,
                        'dy': 0,
                        'dz': -32,
                    },
                    {
                        'structure': 'town1',
                        'rotation': 'CLOCKWISE_90',
                        'mirror': 'NONE',
                        'dx': 31,
                        'dy': 0,
                        'dz': -32,
                    },
                    {
                        'structure': 'town1',
                        'rotation': 'CLOCKWISE_180',
                        'mirror': 'NONE',
                        'dx': 31,
                        'dy': 0,
                        'dz': 31,
                    },
                    {
                        'structure': 'town1',
                        'rotation': 'COUNTERCLOCKWISE_90',
                        'mirror': 'NONE',
                        'dx': -32,
                        'dy': 0,
                        'dz': 31,
                    }
                ],
                'largehouse1': 'self.largehouse1',
            }
    
    def build(self, user, trigger, args):
        """!build <structurename> [offset_x] [offset_y] [offset_z]  places a structure at the given, optional offset"""
        
        if args and len(args) > 0:
            name, dx, dy, dz = self.parse_args(args, ['none', 0, 0, 0])
        else:
            structures = self.server_structures()
            self.msg(user, "available structures [{structs}]".format(structs=", ".join(structures)))
            return
            
        userinfo = self.get_user_info(user)
        x,y,z = self.extract_user_position(userinfo, roundPosition=True)
        x += dx
        y += dy
        z += dz
        
        self.structure((x,y,z), name, 'NONE')
    
    def buildplan(self, user, trigger, args):
        """!buildplan <planname> [deltaX] [deltaY] [deltaZ] [plan args...] builds multiple structures in a planned way"""
        
        if args and len(args) > 0:
            name, dx, dy, dz, *planargs = self.parse_args(args, ['none', 0, 0, 0])
            userinfo = self.get_user_info(user)
            x,y,z = self.extract_user_position(userinfo, roundPosition=True)
            x += dx
            y += dy
            z += dz
        else:
            self.msg(user, "available plans [{plans}]".format(plans=", ".join(self.plans.keys())))
            return
        
        if not self.plans.get(name):
            self.msg(user, 'No plan named '+name)
            self.msg(user, "available plans [{plans}]".format(plans=", ".join(self.plans.keys())))
            return
            
        if type(self.plans[name]) == list:
            plans = self.plans[name]
        elif type(self.plans[name]) == str:
            fun = eval(self.plans[name])
            fun(self, user, userinfo, *planargs)
            plans = []
        else:
            self.msg(user, 'an error occurrrrrrrrrr32938u642893649asdfsdfo3d')
            return
            
        for struct in plans:
            self.structure(
                (x+dx+struct.get('dx', 0), y+dy+struct.get('dy', 0), z+dz+struct.get('dz', 0)),
                struct['structure'],
                struct.get('rotation', 'NONE')
            )

    def structure(self, coords, name, rotation='NONE', mirror='NONE'):
        """ place a structure
        coords: (x,y,z) tuple
        name: name of structure
        rotation: NONE, CLOCKWISE_90, CLOCKWISE_180, COUNTERCLOCKWISE_90
        mirror: NONE, LEFT_RIGHT, or FRONT_BACK """

        if not ':' in name:
            name = "minecraft:"+name
            
        x, y, z = coords
            
        self.setblock(x, y+1, z, 'minecraft:structure_block[mode=load]{metadata: "", mirror: "%s", ignoreEntities: 0b, powered: 0b, seed: 0L, author: "", rotation: "%s", posX: 0, mode: "LOAD", posY: -2, sizeX: 0, posZ: 0, integrity: 1.0f, showair: 0b, name: "%s", id: "minecraft:structure_block", sizeY: 0, sizeZ: 0, showboundingbox: 0b}' % (mirror, rotation, name))
        self.setblock(x, y, z, 'minecraft:redstone_block')
        
    def largehouse1(self, user, userinfo, *planargs):
        x,y,z = self.extract_user_position(userinfo, roundPosition=True)
        self.fill((x-10, y , z-10), (x+10, y+20, z+10), 'minecraft:air', 'destroy')
        for i in range(-10, 10):
            if i % 5 == 0:
                self.structure((x+i-1,y,z+10), 'fence_column')
            else:
                self.structure((x+i,y,z+10), 'fence_wall')
        for i in range(-10, 10):
            if i % 5 == 0:
                self.structure((x+i-1,y,z-10), 'fence_column')
            else:
                self.structure((x+i,y,z-10), 'fence_wall')
        for i in range(-10, 10):
            if i % 5 == 0:
                self.structure((x-10-1,y,z+i), 'fence_column')
            else:
                self.structure((x-10,y,z+i), 'fence_wall')
        for i in range(-10, 10):
            if i % 5 == 0:
                self.structure((x+10-1,y,z+i), 'fence_column')
            else:
                self.structure((x+10,y,z+i), 'fence_wall')
        
        #self.structure((x,y,z), 'cl_huge_house')
        #self.structure((x+5,y,z+5), 'cl_horse_house', rotation='CLOCKWISE_180')
        #self.structure((x-5,y,z-5), 'cl_garden')
        
    def captureplan(self, user, trigger, args):
        """!captureplan <planname> <x> <y> <z> <x> <y> <z>  save a large area into multiple nbt structure files and create a plan for creating it again """
        if args and len(args) > 0:
            if len(args.split(' ')) != 7:
                self.msg(user, "invalid syntax")
                return
            name, x1, y1, z1, x2, y2, z2 = self.parse_args(args, ['none', 0, 0, 0, 0, 0, 0])
        else:
            self.msg(user, "syntax !captureplan <planname> <x> <y> <z> <x> <y> <z>")
            return
        
        # order the limits so that I can start from the lowest x, y, z
        x1, x2 = sorted((x1,x2))
        y1, y2 = sorted((y1,y2))
        z1, z2 = sorted((z1,z2))
        # calculate the size
        dx = x2 - x1
        dy = y2 - y1
        dz = z2 - z1
        area = dx*dy*dz
        if area > 25000000:
            self.msg(user, "I'm not ready to handle more than 25 million blocks yet.")
            return
            
        # now that we have "the area", we need to create a plan to capture it.
        stride_size = 48
        plan = []
        # we should probably start from the x1,y1,z1 corner and capture our structure, striding in the x direction first, then y, then z
        xi = yi = zi = 0
        for z in range(z1, z2, stride_size):
            dz = stride_size
            if z + stride_size > z2:
                dz = z2 - z + 1
            for y in range(y1, y2, stride_size):
                dy = stride_size
                if y + stride_size > y2:
                    dy = y2 - y + 1
                for x in range(x1, x2, stride_size):
                    dx = stride_size
                    if x + stride_size > x2:
                        dx = x2 - x + 1
                    # name the piece of the structure
                    struct_name = '{name}_{xi}_{yi}_{zi}'.format(name=name, xi=xi, yi=yi, zi=zi)
                    # capture the structure
                    self.capture(user, struct_name, (x,y,z), (dx, dy, dz))
                    plan.append( {
                        'structure': struct_name,
                        'rotation': 'NONE',
                        'mirror': 'NONE',
                        'dx': xi*stride_size, # this is the offset from the initial x, not the size of the structure
                        'dy': yi*stride_size,
                        'dz': zi*stride_size,
                    } )

                    xi += 1
                yi += 1
            zi += 1
            
        
        self.plans[name] = plan
        with open('plans.json', 'w') as fh:
            json.dump(self.plans, fh)
        
    def capture(self, user, name, coords, sizes):
        x, y, z = coords
        dx, dy, dz = sizes
        
        self.setblock(x, y-1, z, 'minecraft:structure_block[mode=save]{{metadata: "", mirror: "NONE", ignoreEntities: 0b, powered: 0b, seed: 0L, author: "{user}", rotation: "NONE", posX: 0, mode: "SAVE", posY: 1, sizeX: {dx}, posZ: 0, integrity: 1.0f, showair: 0b, name: "{name}", id: "minecraft:structure_block", sizeY: {dy}, sizeZ: {dz}, showboundingbox: 0b}}'.format(user=user, name=name, dx=dx, dy=dy, dz=dz))
        self.setblock(x, y-2, z, 'minecraft:redstone_block')
        # now destroy the structure block and the redstone block.
        # TODO: capture and replace the original blocks
        #self.setblock(x, y-1, z, 'minecraft:air')
        #self.setblock(x, y-2, z, 'minecraft:air')
        
if __name__ == "__main__":
    tc = StructuresClient()
    tc.connect("localhost", 55115)
