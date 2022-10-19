from socket import socket
import Pyro4
import socket

if __name__ == '__main__':
    ns = Pyro4.locateNS(host="127.0.0.1")
    uri = ns.lookup("0_" + socket.gethostname())
    peer1 = Pyro4.Proxy(uri)
    peer1.start_buying()