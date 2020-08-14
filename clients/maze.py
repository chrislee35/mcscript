#!/usr/bin/env python
from mcscript import Client
from random import shuffle, randrange

class MazeClient(Client):
    DEFAULT_COMMAND_CALLBACKS = [
        {
            'trigger': 'maze',
            'callback': 'self.generate_maze',
            'mutual': 'last_only',
        },
    ]
    def generate_maze(self, user, trigger, args):
        """!maze [width] [length] [height] [walls_block] [floor_block]"""
        
        userinfo = self.get_user_info(user)
        x,y,z = self.extract_user_position(userinfo, roundPosition=True)
        w, l, height, walls, floor = self.parse_args(args, [12, 20, 3, 'minecraft:hay_block', 'minecraft:grass_block'])
        maze = MazeClient.make_maze(w, l)
        lines = maze.split('\n')
        self.fill((x,y,z), (x+len(lines)-1, y+height-1, z+len(lines[0])-1), 'minecraft:air')
        for i in range(len(lines)):
            for j in range(len(lines[i])):
                self.setblock(x+i, y-1, z+j, floor)
                for k in range(height):
                    if lines[i][j] == ' ':
                        pass
                    else:
                        self.fill((x+i, y, z+j), (x+i, y+height, z+j), walls)

    @staticmethod
    def make_maze(w = 16, h = 8):
        vis = [[0] * w + [1] for _ in range(h)] + [[1] * (w + 1)]
        ver = [["|  "] * w + ['|'] for _ in range(h)] + [[]]
        hor = [["+--"] * w + ['+'] for _ in range(h + 1)]
 
        def walk(x, y):
            vis[y][x] = 1
 
            d = [(x - 1, y), (x, y + 1), (x + 1, y), (x, y - 1)]
            shuffle(d)
            for (xx, yy) in d:
                if vis[yy][xx]: continue
                if xx == x: hor[max(y, yy)][x] = "+  "
                if yy == y: ver[y][max(x, xx)] = "   "
                walk(xx, yy)
 
        walk(randrange(w), randrange(h))
 
        s = ""
        for (a, b) in zip(hor, ver):
            s += ''.join(a + ['\n'] + b + ['\n'])
        return s

if __name__ == "__main__":
    tc = MazeClient()
    tc.connect("localhost", 55115)