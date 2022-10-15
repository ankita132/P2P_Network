import config as cfg
import sys
import random
from multiprocessing import Process
from Peer import Peer
import socket
from threading import Thread
import Pyro4
import os

def check_logistics(jobs):
    # complete this function,
    # check if all buyers / all sellers situation 
    # might include other checks
    return True

def get_peers():
    if(len(sys.argv) < 2):
        print("Please specify the number of nodes")
        exit(-1)

    no_of_nodes = int(sys.argv[1])
    jobs = []
    items = cfg.market_data["items"]
    roles = cfg.market_data["roles"]
    no_of_items = cfg.market_data["items_size"]
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

    for i in range(no_of_nodes):
        peer = Peer(all_nodes[i]["id"], all_nodes[i]["role"], no_of_items, items, host_server, all_nodes)
        jobs.append(peer)
        #jobs.append(node)

    return jobs;

if __name__ == '__main__':
    jobs = get_peers()
    print(os.getcwd())
    try:
        if(check_logistics(jobs)):
            for peer in jobs:
                # make this path universal
                os.chdir("/Users/ankita132/Documents/umass/677/lab/lab1/peers")
                peer.start()
                peer.join()

    except KeyboardInterrupt:
        sys.exit()
