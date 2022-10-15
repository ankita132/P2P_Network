from threading import Thread, Lock
from concurrent.futures import ThreadPoolExecutor
import random
import Pyro4
import Pyro4.naming
import socket

class Peer(Thread):
    def __init__(self, id, role, no_of_items, items, host_server, all_nodes):
        self.id = id
        self.role = role
        self.no_of_items = no_of_items
        self.items = items
        self.ns = self.get_nameserver(host_server)
        self.item = items[random.randint(0, len(items) - 1)]
        self.set_neighbors(all_nodes)
        Thread.__init__(self)
        self.hostname = socket.gethostname()
        self.executor = ThreadPoolExecutor(max_workers=10)

    def set_neighbors(self, all_nodes):
        self.neighbors = random.sample(all_nodes, 3)

    def get_nameserver(self, host_server):
        try:
            return Pyro4.locateNS(host=host_server)
        except Exception as e:
            print(e)

    def run(self):
        try:
            with Pyro4.Daemon(host=self.hostname) as daemon:
                uri = daemon.register(self)
                self.ns.register(self.id, uri)
                print(self.id, self.role, self.item, self.neighbors)
                self.executor.submit(daemon.requestLoop)
                
        except Exception as e:
            print(e)

    @Pyro4.expose
    def lookup(self, buyerID, hopcount, search_path):
        return

    @Pyro4.expose
    def reply(self, sellerID, reply_path):
        return

    @Pyro4.expose
    def buy(self, peerID, path):
        return

    