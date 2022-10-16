import Pyro4

if __name__ == '__main__':
    ns = Pyro4.locateNS(host="127.0.0.1")
    for i in range(6):
        uri = ns.lookup(str(i)+ "_Ankitas-MacBook-Pro.local")
        peer1 = Pyro4.Proxy(uri)
        peer1.send_message_to_neighbors("hello you can listesn right")
    #peer1.lookup("0_Ankitas-MacBook-Pro.local", )