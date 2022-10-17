import config as cfg
import sys
import random
from Peer import Peer
import socket
import Pyro4
from multiprocessing import Process
from threading import Thread
import os

def check_logistics(jobs):
    # complete this function,
    # check if all buyers / all sellers situation 
    # might include other checks
    return True

def process_func(all_nodes, no_of_items, items, max_items, host_server, i):
    print(os.getpid())
    peer = Peer(all_nodes[i]["id"], all_nodes[i]["role"], no_of_items, items, max_items, host_server, all_nodes)
    peer.start()
    peer.join()

if __name__ == '__main__':
    #loop 
    print(os.getcwd())
    if(len(sys.argv) < 2):
        print("Please specify the number of nodes")
        sys.exit()

    no_of_nodes = int(sys.argv[1])
    items = cfg.market_data["items"]
    roles = cfg.market_data["roles"]
    no_of_items = cfg.market_data["items_size"]
    max_items = cfg.market_data["max_items"]
    host_server = cfg.local_server
    all_nodes = []

    try:
        ns = Pyro4.locateNS(host=host_server)
    except Exception as e:
        print(e)
    
    for i in range(no_of_nodes):
        role = roles[random.randint(0,len(roles) - 1)]
        id = str(i) + "_" + socket.gethostname()
        all_nodes.append({"id": id, "role": role})
    
    try:
        if(check_logistics(all_nodes)):
            processes = []
            for i in range (0, len(all_nodes)):
                processes.append(Process(target=process_func, args=(all_nodes,no_of_items,items, max_items, host_server,i, )))
                
            for process in processes:
                process.start()
            for process in processes:
                process.join()

    except KeyboardInterrupt:
        sys.exit()
