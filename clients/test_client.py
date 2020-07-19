#!/usr/bin/env python
from mcscript import Client

class TestClient(Client):
    DEFAULT_COMMAND_CALLBACKS = [{
        'trigger': 'test',
        'callback': 'self.test',
        'mutual': 'shared',
    }]
    def test(self, user, trigger, args):
        resp = self.send_cmd('/give {user} minecraft:salmon'.format(user=user))
        print(resp)
        
    def on_connect(self):
        resp = self.send_cmd('/say test module is online')
        print(resp)

if __name__ == "__main__":
    tc = TestClient()
    tc.connect("localhost", 55115)