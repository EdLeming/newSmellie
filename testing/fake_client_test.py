from xmlrpclib import ServerProxy
if __name__ == "__main__":
    client = ServerProxy("http://localhost:5020")
    print "RUN IN NORMAL MODE:"
    print client.fake_method("hello")
    print "RUN IN DUMMY_MODE"
    print client.go_dummy_mode()
    print client.fake_method("in dummy mode")
    print client.fake_raise_exception()