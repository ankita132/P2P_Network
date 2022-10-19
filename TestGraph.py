import socket
import config as cfg
import test

mapped_neighbors = [[1,2], [4,5], [3,5], [0,4,5], [0,1], [0,4]]
mapped_roles = ["BUY", "SELL", "BUY", "BUY", "SELL", "SELL"]
mapped_items = ["FISH", "SALT", "BOAR", "SALT", "SALT", "BOAR"]

def test_graph():
    all_nodes = []
    no_of_items = cfg.market_data["items_size"]
    host_server = cfg.local_server
    items = cfg.market_data["items"]
    for i in range(6):
        role = mapped_roles[i]
        id = str(i) + "_" + socket.gethostname()
        neighbors = []
        for idx in mapped_neighbors[i]:
            neighbors.append(str(idx) + "_" + socket.gethostname())
        all_nodes.append({"id": id, "role": role, "neighbors": neighbors})

    return all_nodes,no_of_items,items,host_server
    


