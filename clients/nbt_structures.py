#!/usr/bin/env python
from mcscript import Client
#import nbtlib
import os

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
        
    ]
    
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
            ]
        }
        
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
        elif callable(self.plans[name]):
            plans = self.plans[name](*planargs)
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
        
        
if __name__ == "__main__":
    tc = StructuresClient()
    tc.connect("localhost", 55115)
