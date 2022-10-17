from threading import Thread, Lock
from concurrent.futures import ThreadPoolExecutor
import random
import Pyro4
import Pyro4.naming
import socket
import time
import copy
import sys

class Peer(Thread):
    def __init__(self, id, role, no_of_items, items, host_server, all_nodes):
        self.id = id
        self.role = role
        self.current_items = no_of_items
        self.total_items = no_of_items
        self.items = items
        self.ns = self.get_nameserver(host_server)
        self.item = self.get_random_item()
        self.neighbors = {}
        self.all_nodes = all_nodes
        self.seller_list_lock = Lock()
        self.itemlock = Lock()
        Thread.__init__(self)
        self.hostname = socket.gethostname()
        self.executor = ThreadPoolExecutor(max_workers=20)
        self.sellers = []
    
    def get_random_item(self):
        return self.items[random.randint(0, len(self.items) - 1)]

    def get_neighbors(self):
        # neighbors set 1 to 3
        list = filter(lambda val: val["id"] != self.id, random.sample(self.all_nodes, 3))

        neighbors = {}
        for neighbor in list:
            neighbors[neighbor["id"]] = self.ns.lookup(neighbor["id"])

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

                #daemon.requestLoop()
                self.executor.submit(daemon.requestLoop)
                time.sleep(1)

                self.neighbors = self.get_neighbors()
                print(self.id, self.role, self.item, self.neighbors)

                while True and self.role == "BUY":
                    lookup_requests = []
                    neighbors_copy = copy.deepcopy(self.neighbors)

                    for neighbor_id in neighbors_copy:
                        with Pyro4.Proxy(neighbors_copy[neighbor_id]) as neighbor:
                            search_path = [self.id]
                            print(time.time(), self.id, "issues a lookup to", neighbor_id, "for", self.item)
                            
                            lookup_requests.append(self.executor.submit(neighbor.lookup, self.id, self.item, 4, search_path))
                    
                    for lookup_request in lookup_requests:
                        lookup_request.result()

                    # with self.seller_list_lock:
                    #     if self.sellers:
                    #         random_seller_id = self.sellers[random.randint(0, len(self.sellers) - 1)]

                    #         with Pyro4.Proxy(self.ns.lookup(random_seller_id)) as seller:
                    #             future = self.executor.submit(seller.buy, self.id)

                    #             if future.result():
                    #                 print(time.time(), self.id, "bought", self.good, "from", random_seller_id)
                    #             else:
                    #                 print(time.time(), self.id, "failed to buy", self.good, "from", random_seller_id)

                    #     self.sellers = []
                    #     self.good = self.get_random_item()
                    
                    time.sleep(1)

                while True:
                    time.sleep(1)
                
        except Exception as e:
            template = "An exception of type {0} occurred at run. Arguments:\n{1!r}"
            message = template.format(type(e).__name__, e.args)
            print(message)

    @Pyro4.expose
    def establish_message(self, message):
        print(self.id, self.role, message, "do something")

    @Pyro4.expose
    def send_message_to_neighbors(self, message):
        neighbors_copy = copy.deepcopy(self.neighbors)
        for neighbor_id in neighbors_copy:
            try:
                neighbor = Pyro4.Proxy(neighbors_copy[neighbor_id])
                self.executor.submit(neighbor.establish_message, message)
            except Exception as e:
                print("An exception occured at send_message_to_neighbors")
                print(e)

    @Pyro4.expose
    def send_message_to_neighbors_hopcount(self, message, hopcount):
        hopcount -= 1
        print(hopcount)

        if(hopcount == 0): 
            self.executor.submit(self.send_message_to_neighbors, message)
            return

        neighbors_copy = copy.deepcopy(self.neighbors)

        for neighbor_id in neighbors_copy:
            try:
                neighbor = Pyro4.Proxy(neighbors_copy[neighbor_id])
                self.executor.submit(neighbor.send_message_to_neighbors_hopcount, message, hopcount)
            except Exception as e:
                print("An exception occured at send_message_to_neighbors_hopcount")
                print(e)

        self.executor.submit(self.send_message_to_neighbors_hopcount, message, hopcount)

    @Pyro4.expose
    def lookup(self, buyer_id, product_name, hopcount, search_path):
        hopcount -= 1

        if hopcount <= 0:
            return
        
        last_peer_id = search_path[-1]
        try:
            if self.role == "SELL" and product_name == self.item and self.current_items > -1:
                with Pyro4.Proxy(self.ns.lookup(last_peer_id)) as recipient:
                    search_path.pop()
                    search_path.insert(0, self.id)
                    self.executor.submit(recipient.reply, self.id, search_path)
            else:
                neighbors_copy = copy.deepcopy(self.neighbors)

                for neighbor_location in neighbors_copy:
                    if neighbor_location != last_peer_id:
                        with Pyro4.Proxy(neighbors_copy[neighbor_location]) as neighbor:
                            if self.id not in search_path:
                                search_path.append(self.id)
                            self.executor.submit(neighbor.lookup, buyer_id, product_name, hopcount, search_path)

        except(Exception) as e:
            print("Error occurred at lookup")
            print(e)


    @Pyro4.expose
    def reply(self, sellerID, reply_path):
        print("here")
        # try:
        #     if reply_path and len(reply_path) == 1:
        #         print(time.time(), self.id, "got a match reply from", reply_path[0])

        #         with self.seller_list_lock:
        #            self.sellers.extend(reply_path)

        #     elif reply_path and len(reply_path) > 1:
        #         recipient_id = reply_path.pop()
        #         with Pyro4.Proxy(self.neighbors[recipient_id]) as recipient:
        #             self.executor.submit(recipient.reply, self.id, reply_path)

        # except(Exception) as e:
        #     print("Error occurred at reply")
        #     print(e)

    @Pyro4.expose
    def buy(self, peerID, path):
        with self.itemlock:
            if self.current_items > 0:
                self.current_items -= 1
                # print(time.time(), peer_id, "purchased", self.good, "from", self.id, self.n_items, "remains now")
                return True
            # No more items to sell, randomly pick up another item
            else:
                # print(time.time(), peer_id, "failed to purchase", self.good)
                self.item = self.get_random_item()
                self.current_items = self.total_items
                print(time.time(), self.id, "now sells", self.current_items, self.item)
                return False

    