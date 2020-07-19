# mcscript (Minecraft Script)

MCScript wraps the Java Minecraft server console and allows for scripts to be run and triggered by events.

## Server-side Design

### MCLauncher
MCLauncher starts the Java Minecraft server and monitors the logs.  It also receives commands from the MCScriptClientRequestHandlers.

### MCScriptServer
The MCScriptServer is a threaded TCP server, defaults to localhost:55115.  It receives connections from MCScript Clients and generates a MCScriptClientRequestHandler for each client.  It also routes "triggers" to the registered MCScriptClientRequestHandler.  See the section on triggers.

### MCScriptClientRequestHandler
This handles the communication from and to Clients.  Clients must register any trigger words that they want to be called back on.  Clients can also send commands to the MCScriptClientRequestHandler.  The communications is simply a 4-byte packed length field followed by a JSON blob.

## Client-side Design
Most of the intelligent parts of the API are in the Client class, with clients subclassing the Client class.  This design choice, i.e., putting the complexity in the Client class, was to simplify the Server implementation and to avoid constant restarting of the Minecraft server in response to new features.


### Example Client

    #!/usr/bin/env python
    from mcscript import Client
    import math, random

    class TestClient(Client):
        DEFAULT_COMMAND_CALLBACKS = [{
            'trigger': 'test',
            'callback': 'self.test',
            'mutual': 'shared',
        }]
        # all callbacks must have these parameters
        def test(self, user, trigger, args):
            # give the player a salmon
            resp = self.send_cmd('/give {user} minecraft:salmon'.format(user=user))
            # find the location of a player
            userinfo = self.get_user_info(user)
            x,y,z = self.extract_user_position(userinfo, roundPosition=True)
            
            # drop an anvil on their head
            facing = random.choice(['north','south','east','west'])
            self.setblock(x, y+20, z, "minecraft:chipped_anvil", facing=facing)
            
            # spawn a charged creeper 15 blocks from them in a random direction from the player
            angle = random.randint(0, 360)
            dx = int(15*math.cos(angle*math.pi/180))
            dz = int(15*math.sin(angle*math.pi/180))
            self.summon(x+dx, y, z+dz, "minecraft:creeper", powered=1)
            
            # tell them that you love them
            self.send_cmd('/msg {user} Happy Birthday...')
        
        def on_connect(self):
            # tell the world that you're here
            resp = self.send_cmd('/say test module is online, type !test for a surprise')
            print(resp)

    if __name__ == "__main__":
        tc = TestClient()
        tc.connect("localhost", 55115)


## Triggers

Triggers are simply keywords that players can type in to trigger a callback to the registered client(s).  Triggers can be registered in one of three mutual roles: shared, first_only, last_only.  This dictates if multiple clients can register the same keyword or not and what should happen if a client tries to register a keyword owned by another client.  Note, that if you use first_only and your client stops for whatever reason, you may have to trigger the server to notice the dead connection and have the previous client deregistered before the new client can register.  I recommend using shared and last_only.




