import Pyro4

if __name__ == '__main__':
    ns = Pyro4.locateNS(host="127.0.0.1")
    uri = ns.lookup("0_Ankitas-MacBook-Pro.local")
    peer1 = Pyro4.Proxy(uri)
    peer1.establish_message("hello you can listesn right")