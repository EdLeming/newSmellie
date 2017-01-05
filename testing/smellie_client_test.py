from xmlrpclib import ServerProxy

if __name__ == "__main__":
    client = ServerProxy("http://localhost:5020")
    print client.set_gain_control(0.6)