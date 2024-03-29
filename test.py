# check test cases

from socket import socket
import Pyro4
import socket
import unittest
import config as cfg

class test_network(unittest.TestCase):
    # check if network is running correctly with every buyer having a possible seller case
    def test_successful_buy_sell(self):
        ns = Pyro4.locateNS(host=cfg.local_server)
        i = 0
        uri = ns.lookup(str(i) + "_" + socket.gethostname())
        peer1 = Pyro4.Proxy(uri)
        isBought, timetaken = peer1.start_buying()
        self.assertEqual(isBought,True)
    
    # check if a buyer has no corresponding seller, then no transaction takes place
    def test_seller_not_present(self):
        ns = Pyro4.locateNS(host=cfg.local_server)
        i = 2
        uri = ns.lookup(str(i) + "_" + socket.gethostname())
        peer = Pyro4.Proxy(uri)
        isBought, timetaken = peer.start_buying()
        self.assertEqual(isBought,False)

    # check count of items of a seller decreases after every transaction
    def test_decreasing_item_count(self):
        ns = Pyro4.locateNS(host=cfg.local_server)
        i = 0
        uri = ns.lookup(str(i) + "_" + socket.gethostname())
        peer1 = Pyro4.Proxy(uri)
        current_item_count = peer1.get_current_item_values()
        isBought, timetaken = peer1.start_buying()
        current_item_count_after_buy = peer1.get_current_item_values()
        self.assertEqual(current_item_count, current_item_count_after_buy)

    # check if count of items of seller goes to zero, then it is updated with new item count of new item
    def test_item_count_update_after_exhaustion(self):
        ns = Pyro4.locateNS(host=cfg.local_server)
        i = 0
        uri = ns.lookup(str(i) + "_" + socket.gethostname())
        peer1 = Pyro4.Proxy(uri)
        current_item_count = peer1.get_current_item_values()
        
        for val in range(0, 10):
            isBought, timetaken = peer1.start_buying()

        current_item_count_after_buy = peer1.get_current_item_values()
        self.assertEqual(current_item_count, current_item_count_after_buy)

    

if __name__ == '__main__':
    unittest.main()