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
        userinfo = self.get_user_info(user)
        x,y,z = self.extract_user_position(userinfo, roundPosition=True)
        w = 12
        l = 20
        walls = 'minecraft:hay_block'
        floor = 'minecraft:grass_block'
        if args and len(args) > 0:
            pargs = args.split(' ')
            if len(pargs) > 0:
                w = int(pargs[0])
            if len(pargs) > 1:
                l = int(pargs[1])
            if len(pargs) > 2:
                walls = pargs[2]
            if len(pargs) > 3:
                floor = pargs[3]
        maze = MazeClient.make_maze(w, l)
        lines = maze.split('\n')
        for i in range(len(lines)):
            for j in range(len(lines[i])):
                self.setblock(x+i, y-1, z+j, floor)
                for k in range(3):
                    if lines[i][j] == ' ':
                        self.setblock(x+i, y+k, z+j, 'minecraft:air')
                    else:
                        self.setblock(x+i, y+k, z+j, walls)

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