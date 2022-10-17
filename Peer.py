from threading import Thread, Lock
from concurrent.futures import ThreadPoolExecutor
import random
import Pyro4
import Pyro4.naming
import socket
import time

class Peer(Thread):
    def __init__(self, id, role, no_of_items, items, host_server, all_nodes):
        self.id = id
        self.role = role
        self.no_of_items = no_of_items
        self.items = items
        self.ns = self.get_nameserver(host_server)
        self.item = items[random.randint(0, len(items) - 1)]
        self.neighbors = []
        self.all_nodes = all_nodes
        Thread.__init__(self)
        self.hostname = socket.gethostname()
        self.executor = ThreadPoolExecutor(max_workers=10)
        self.sellers = []

    def get_neighbors(self):
        # neighbors set 1 to 3
        list = filter(lambda val: val["id"] != self.id, random.sample(self.all_nodes, 3))

        neighbors = []
        for neighbor in list:
            neighbors.append(neighbor["id"])

        return neighbors

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

                self.neighbors = self.get_neighbors()
                print(self.id, self.role, self.item, self.neighbors)
                #daemon.requestLoop()
                self.executor.submit(daemon.requestLoop)

                while True and self.role == "BUY":
                    #print("lol")
                    time.sleep(1)

                while True:
                    time.sleep(1)
                
        except Exception as e:
            print(e)

    @Pyro4.expose
    def establish_message(self, message):
        print(self.id, self.role, message, "do something")

    @Pyro4.expose
    def send_message_to_neighbors(self, message):
        print(self.id)
        for neighbor_id in self.neighbors:
            neighbor_uri = self.ns.lookup(neighbor_id)
            neighbor = Pyro4.Proxy(neighbor_uri)
            neighbor.establish_message(message)

    @Pyro4.expose
    def lookup(self, product_name, hopcount, id_list):
        return

    @Pyro4.expose
    def reply(self, sellerID, reply_path):
        return

    @Pyro4.expose
    def buy(self, peerID, path):
        return

    