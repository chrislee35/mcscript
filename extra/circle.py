#!/usr/bin/env python3
import math

def spiral(start_point, direction, size=20, levels=4, span=3, block='minecraft:white_terracotta'):
    center = start_point
    center[0] += direction[0] + int(size/2)
    center[2] += direction[2] + int(size/2)
    
    last_x = 0
    last_z = 0
    
    for level in range(levels):
        for angle in range(360):
            delta_x = int(direction[0] * size * math.cos(math.pi*angle/180))
            delta_y = direction[1] * ((level * span) + int(span * angle/360))
            delta_z = int(direction[2] * size * math.sin(math.pi*angle/180))
            
            if last_x == delta_x and last_z == delta_z:
                continue
            last_x = delta_x
            last_z = delta_z
                
            print("/setblock {x} {y} {z} {block}".format(x=center[0]+delta_x, y=center[1]+delta_y, z=center[2]+delta_z, block=block))
            
    
start_point = [418, 63, 6]
direction = (1, 1, -1)

spiral(start_point, direction)
