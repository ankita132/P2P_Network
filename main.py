import config as cfg
import sys
import random
from Peer import Peer
import socket
import Pyro4
from multiprocessing import Process
import os
from threading import Thread

def server_identity():
    return "_" + socket.gethostname()

def bfs(all_nodes, root):
    maxdepth = 0
    visited = []
    queue = []
    visited.append(root)
    queue.append((root,1))
    while queue:
        x,depth = queue.pop(0)
        maxdepth = max(maxdepth,depth)
        for child in all_nodes[x]["neighbors"]:
            index = int(child.replace(server_identity(), ""))
            if index not in visited:
                visited.append(index)
                queue.append((index,depth+1))
    return maxdepth

def graph_util(v, all_nodes):
    visited = set()
    stack = [v]
    while stack:
        src = stack.pop()
        visited.add(src)
        for val in all_nodes[src]["neighbors"]:
            index = int(val.replace(server_identity(), ""))
            if index not in visited:
                stack.append(index)
    return len(visited) == len(all_nodes)

def check_graph_connected(all_nodes):
    for i in range(0, len(all_nodes)):
        if(graph_util(i, all_nodes)):
            return True
    return False

def get_max_depth(all_nodes):
    max_depth = 0
    for i in range(0, len(all_nodes)):
        max_depth = max(max_depth, bfs(all_nodes, i))

    return max_depth

def check_logistics(all_nodes):
    is_all_buy= True 
    is_all_sell = True
    is_connected = check_graph_connected(all_nodes)
    for node in all_nodes:
        if(node["role"] == "BUY"):
            is_all_sell = False
        elif(node["role"] == "SELL"):
            is_all_buy = False

    return not(is_all_buy) and not(is_all_sell) and is_connected

def process_func(all_nodes, no_of_items, items, host_server, i, hopcount):
    #print(os.getpid())
    os.chdir("/")
    peer = Peer(all_nodes[i]["id"], all_nodes[i]["role"], no_of_items, items, host_server, all_nodes, all_nodes[i]["neighbors"], hopcount)
    peer.start()
    peer.join()

def get_nodes():
    if(len(sys.argv) < 2):
        print("Please specify the number of nodes")
        sys.exit()

    no_of_nodes = int(sys.argv[1])
    items = cfg.market_data["items"]
    roles = cfg.market_data["roles"]
    no_of_items = cfg.market_data["items_size"]
    host_server = cfg.local_server
    all_nodes = []

    try:
        ns = Pyro4.locateNS(host=host_server)
    except Exception as e:
        print('No nameserver found, starting new namserver')
        Thread(target=Pyro4.naming.startNSloop, kwargs={"host": host_server}).start()
    
    for i in range(no_of_nodes):
        random_ids = random.sample(range(0, no_of_nodes-1), 3)
        neighbors = []
        for id in random_ids:
            if(id != i):
                neighbors.append(str(id) + server_identity())

        role = roles[random.randint(0,len(roles) - 1)]
        id = str(i) + server_identity()
        all_nodes.append({"id": id, "role": role, "neighbors": neighbors})

    return all_nodes,no_of_items,items, host_server

if __name__ == '__main__':
    try:
        while True:
            all_nodes,no_of_items,items, host_server = get_nodes()
            if(check_logistics(all_nodes)): break

        hopcount = get_max_depth(all_nodes)-1
        processes = []
        for i in range (0, len(all_nodes)):
            processes.append(Process(target=process_func, args=(all_nodes,no_of_items,items, host_server,i, hopcount)))
                
        for process in processes:
            process.start()
        for process in processes:
            process.join()

    except KeyboardInterrupt:
        sys.exit()
