from server.smellie_server import SmellieServer
import smellie_config

class FakeClass(object):
    def fake_method(self, message):
        return "I got called with " + message

    def fake_raise_exception(self):
        raise ValueError
        return 0
        
    def go_dummy_mode(self, dummy_on = True):
        smellie_config.DUMMY_MODE = dummy_on
        return 0
        
if __name__ == "__main__":
    server = SmellieServer("0.0.0.0", 5020)
    server.register(FakeClass())
    server.serve_forever()