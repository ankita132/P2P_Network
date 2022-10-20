from socket import socket
import Pyro4
import socket
import unittest
import config as cfg

class test_network(unittest.TestCase):
    def test_no_item_seller(self):
        ns = Pyro4.locateNS(host=cfg.local_server)
        i = 0
        uri = ns.lookup(str(i) + "_" + socket.gethostname())
        peer1 = Pyro4.Proxy(uri)
        self.assertEqual(peer1.start_buying(),False)
        print("No seller found for buyer {}".format(i))

    # def test_all_item_seller(self):
    #     mapped_roles = ["BUY", "SELL", "BUY", "BUY", "SELL", "SELL"]
    #     mapped_items = ["FISH", "SALT", "BOAR", "SALT", "FISH", "BOAR"] 
    #     ns = Pyro4.locateNS(host="127.0.0.1")
    #     i = 0
    #     uri = ns.lookup(str(i) + "_" + socket.gethostname())
    #     peer1 = Pyro4.Proxy(uri)
    #     self.assertEqual(peer1.start_buying(),True)
    #     print("sellers found for all buyers")

    # def test_decreasing_item_count(self):
    #     # mapped_roles = ["BUY", "SELL", "BUY", "BUY", "SELL", "SELL"]
    #     # mapped_items = ["SALT", "SALT", "SALT", "SALT", "FISH", "BOAR"] 
    #     ns = Pyro4.locateNS(host="127.0.0.1")
    #     for i in [0,2,3]:
    #         uri = ns.lookup(str(i) + "_" + socket.gethostname())
    #         peer1 = Pyro4.Proxy(uri)
    #         peer1.start_buying()
    #     print("Item count decreases by 1 after each sell")
    

if __name__ == '__main__':
    unittest.main()