from socket import socket
import Pyro4
import socket

if __name__ == '__main__':
    ns = Pyro4.locateNS(host="127.0.0.1")
    for i in range(6):
        uri = ns.lookup(str(i)+"_" + socket.gethostname())
        peer1 = Pyro4.Proxy(uri)
        peer1.send_message_to_neighbors("hello you can listesn right")
    # 
    # 
    # peer1.lookup("2_Ankitas-MacBook-Pro.local", "SALT", 5, [])
    #peer1.lookup("0_Ankitas-MacBook-Pro.local", )