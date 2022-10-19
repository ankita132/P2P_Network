from cgitb import lookup
import socket
from threading import Thread, Lock
from concurrent.futures import ThreadPoolExecutor
import random
import Pyro4
import Pyro4.naming
import time
import copy
import sys
import datetime
import config as cfg
from tests.TestGraph import mapped_items

class Peer(Thread):
    def __init__(self, id, role, no_of_items, items, host_server, all_nodes, neighbor_ids, hopcount):
        self.id = id
        self.role = role
        self.current_items = no_of_items
        self.total_items = no_of_items
        self.items = items
        self.ns = self.get_nameserver(host_server)
        self.item = self.get_random_item()
        self.neighbors = {}
        self.all_nodes = all_nodes
        self.neighbor_ids = neighbor_ids
        self.seller_list_lock = Lock()
        self.itemlock = Lock()
        Thread.__init__(self)
        self.hostname = host_server
        self.executor = ThreadPoolExecutor(max_workers=10)
        self.sellers = []
        self.requests = 0
        self.hopcount = hopcount
    
    def get_random_item(self):
        if(cfg.env == "TEST"):
            i = int(self.id.replace("_" + socket.gethostname(), ""))
            return mapped_items[i]
        return self.items[random.randint(0, len(self.items) - 1)]


    def get_neighbors(self):
        neighbors = {}
        for neighbor_id in self.neighbor_ids:
            neighbors[neighbor_id] = self.ns.lookup(neighbor_id)

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
                self.executor.submit(daemon.requestLoop)
                time.sleep(1)

                self.neighbors = self.get_neighbors()
                print(self.id, self.role, self.item, self.neighbors)
                if(cfg.env == "TEST"):
                    self.start_buy_sell_test()
                else:
                    self.start_buy_sell()
                
        except Exception as e:
            print("Error occurred at run function")
            print(e)

    @Pyro4.expose
    def start_buying(self):
        isBought = False
        print("{} Buyer {} is requesting to buy {}".format(datetime.datetime.now(), self.id.split('_')[0], self.item))
        neighbors_copy = copy.deepcopy(self.neighbors)
        lookup_requests = []

        for neighbor_id in neighbors_copy:
            with Pyro4.Proxy(neighbors_copy[neighbor_id]) as neighbor:
                search_path = [self.id]
                print("{} Buyer {} issued a lookup to neighbour {} for item {}".format(datetime.datetime.now(), self.id.split('_')[0], neighbor_id.split('_')[0], self.item))
                lookup_requests.append(self.executor.submit(neighbor.lookup, self.id, self.item, self.hopcount, search_path))
                   
        for lookup_request in lookup_requests:
            lookup_request.result()
        
        with self.seller_list_lock:
            if self.sellers:
                random_seller_id = self.sellers[random.randint(0, len(self.sellers) - 1)]
                with Pyro4.Proxy(self.ns.lookup(random_seller_id)) as seller:
                    future = self.executor.submit(seller.buy, self.id)
                    if future.result():
                        print("{} Buyer {} bought {} from Seller {}".format(datetime.datetime.now(), self.id.split('_')[0], self.item, random_seller_id.split('_')[0]))
                        isBought = True
                    else:
                        print("{} Buyer {} failed to buy {} from Seller {}".format(datetime.datetime.now(), self.id.split('_')[0], self.item, random_seller_id.split('_')[0]))
                        isBought = False
            self.sellers = []
            print("\n")
            self.item = self.get_random_item()

            return isBought

    def start_buy_sell_test(self):
        if(self.role == "BUY"):
            if self.role == "BUY":
                for i in range(cfg.MAX_REQUESTS):
                    self.start_buying()
                time.sleep(1)

        while True and self.role == "SELL":
            time.sleep(1)

    def start_buy_sell(self):
        while True and self.role == "BUY":
            self.start_buying()  
            time.sleep(1)

        while True and self.role == "SELL":
            time.sleep(1)

    @Pyro4.expose
    def establish_message(self, message):
        print(self.id, self.role, message, "message established")

    @Pyro4.expose
    def send_message_to_neighbors(self, message):
        neighbors_copy = copy.deepcopy(self.neighbors)
        for neighbor_id in neighbors_copy:
            try:
                neighbor = Pyro4.Proxy(neighbors_copy[neighbor_id])
                self.executor.submit(neighbor.establish_message, message)
            except Exception as e:
                print("Error occured at send_message_to_neighbors")
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
                print("Error occured at send_message_to_neighbors_hopcount")
                print(e)

        self.executor.submit(self.send_message_to_neighbors_hopcount, message, hopcount)

    @Pyro4.expose
    def lookup(self, buyer_id, product_name, hopcount, search_path):
        hopcount = hopcount - 1
        if hopcount < 0:
            #print("Done with hopping for ", buyer_id, "to buy ", product_name)
            return
        last_peer_id = search_path[-1]
        try:
            if self.role == "SELL" and product_name == self.item and self.current_items > 0:
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

        except Exception as e:
            print("Error occurred at lookup")
            print(e)


    @Pyro4.expose
    def reply(self, sellerID, reply_path):
        try:
            if reply_path and len(reply_path) == 1:
                print("{} Buyer {} received a reply from Seller {}".format(datetime.datetime.now(), self.id.split('_')[0], sellerID.split('_')[0]))
                with self.seller_list_lock:
                   self.sellers.extend(reply_path)

            elif reply_path and len(reply_path) > 1:
                recipient_id = reply_path.pop()
                with Pyro4.Proxy(self.ns.lookup(recipient_id)) as recipient:
                    self.executor.submit(recipient.reply, sellerID, reply_path)
            
            else:
                print("The reply path is empty")

        except(Exception) as e:
            print("Error occured at reply")
            print(e)

    @Pyro4.expose
    def buy(self, peer_id):
        with self.itemlock:
            if self.current_items > 0:
                self.current_items -= 1
                print("{} Seller {} has {} items of {} remaining after selling to Buyer {}".format(
                    datetime.datetime.now(), self.id.split('_')[0], self.current_items, self.item, peer_id.split('_')[0]))
            # if seller has no more remaining items to sell, chose another item randomly to sell
                if self.current_items == 0:
                    self.item = self.get_random_item()
                    self.current_items = self.total_items
                    print("{} Seller {} now sells {} items of {}".format(datetime.datetime.now(), self.id.split('_')[0], self.current_items, self.item))
                return True
            

    