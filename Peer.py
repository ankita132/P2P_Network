from threading import Thread, Lock
from concurrent.futures import ThreadPoolExecutor
import random
import Pyro4
import Pyro4.naming
import socket
import copy
import time

class Peer(Thread):
    def __init__(self, id, role, no_of_items, items, max_items, host_server, all_nodes):
        self.id = id
        self.role = role
        self.no_of_items = no_of_items
        self.max_items = max_items
        self.items = items
        self.ns = self.get_nameserver(host_server)
        self.item = items[random.randint(0, len(items) - 1)]
        self.neighbors = []
        self.all_nodes = all_nodes
        Thread.__init__(self)
        self.hostname = socket.gethostname()
        self.executor = ThreadPoolExecutor(max_workers=10)
        self.item_sellers = []
        self.item_seller_list_lock = Lock()
        self.item_lock = Lock()
        self.hopcount = 3

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
                self.executor.submit(daemon.requestLoop)

                while True and self.role == "BUY":
                    neighbors_copy = copy.deepcopy(self.neighbors)
                    for neighbor_id in neighbors.copy:
                        neighbor_uri = self.ns.lookup(neighbor_id)
                        with Pyro4.Proxy(neighbor_uri) as neighbor:
                            search_path = [self.id]
                            print(time.time(),"{} has called lookup to buy {} in neighbor {}".format(self.id,self.item,neighbor_id))
                            self.executor.submit(neighbor.lookup,self.id,self.item,self.hopcount,search_path)
                with self.item_seller_list_lock:
                    if len(self.item_sellers)>0:
                        seller_id_pick = self.item_sellers[random.randint(0,len(self.item_sellers)-1)]
                        seller_uri = self.ns.lookup(seller_id_pick)
                        with Pyro4.Proxy(seller_uri) as seller:
                            self.executor.submit(seller.buy,self.id,[])

                    self.item_sellers = []
                    self.item = self.items[random.randint(0, len(self.items) - 1)]

                while True:
                    time.sleep(1)
                
        except Exception as e:
            print(e)

    @Pyro4.expose
    def establish_message(self, message):
        print(self.id, self.role, message)

    @Pyro4.expose
    def send_message_to_neighbors(self, message):
        print(self.id)
        for neighbor_id in self.neighbors:
            neighbor_uri = self.ns.lookup(neighbor_id)
            neighbor = Pyro4.Proxy(neighbor_uri)
            neighbor.establish_message(message)

    @Pyro4.expose
    def lookup(self, buyerID, product_name, hopcount, search_path):
        if hopcount<=0:
           return
        hopcount = hopcount-1
        last_neighbor_id = search_path[-1]
        try:
            if self.role=="SELL" and product_name==self.item and self.no_of_items>0:
                with Pyro4.Proxy(self.ns.lookup(last_neighbor_id)) as receiver:                   
                    search_path = [self.id] + search_path
                    search_path.pop() 
                    self.executor.submit(receiver.reply, self.id, search_path)
            else:
                neighbors_copy = copy.deepcopy(self.neighbors)
                for neighbor_id in neighbors_copy:
                    if neighbor_id == last_neighbor_id:
                        continue
                    neighbor_uri = self.ns.lookup(neighbor_id)
                    with Pyro4.Proxy(neighbor_uri) as neighbor:
                        if self.id not in search_path:
                            searchpath.append(self.id)
                        self.executor.submit(neighbor.lookup, buyerID, product_name, hopcount, search_path)


        except Exception as e:
            print(e)

    @Pyro4.expose
    def reply(self, sellerID, reply_path):
        try:
            if len(reply_path)==1:
                print(time.time(),"{} replied to {}".format(sellerID,self.id))
                with self.item_seller_list_lock:
                    self.item_sellers.extend(sellerID)
            elif len(reply_path)>2:
                receiver_id = reply_path.pop()
                receiver_uri = self.ns.lookup(receiver_id)
                with Pyro4.Proxy(receiver_uri) as receiver:
                    self.executor.submit(receiver.reply,sellerID,reply_path)
        
        except Exception as e:
            print(e)

    @Pyro4.expose
    def buy(self, peerID, path):
        try:
            with self.item_lock:
                if self.no_of_items>0:
                    self.no_of_items = self.no_of_items - 1
                    print(time.time(),"{} bought item {} from {}".format(peerID,self.item,self.id))
                    return True
                else:
                    self.item = self.items[random.randint(0, len(self.items) - 1)]
                    self.no_of_items = self.max_items
                    return False
        except Exception as e:
            print(e)

    