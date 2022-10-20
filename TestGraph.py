import socket
import config as cfg

mapped_items = ["FISH", "SALT", "BOAR", "SALT", "FISH", "BOAR"]
    
def send_tests():
    match cfg.TEST_CASE_NO:
        case 1:
            return test_graph1()
        case 2:
            return test_graph2()
        case 3:
            return test_graph3()
        case 4:
            return test_graph4()
        case 5:
            return test_graph5()
        case 6:
            return test_graph6()

def create_graph(mapped_neighbors, mapped_roles):
    all_nodes = []
    no_of_items = cfg.market_data["items_size"]
    host_server = cfg.local_server
    items = cfg.market_data["items"]
    for i in range(len(mapped_roles)):
        role = mapped_roles[i]
        id = str(i) + "_" + socket.gethostname()
        neighbors = []
        for idx in mapped_neighbors[i]:
            neighbors.append(str(idx) + "_" + socket.gethostname())
        all_nodes.append({"id": id, "role": role, "neighbors": neighbors})
    return all_nodes,no_of_items,items,host_server

def test_graph1():
    mapped_neighbors = [[1,2], [4,5], [3,5], [0,4,5], [0,1], [0,4]]
    mapped_roles = ["BUY", "SELL", "BUY", "BUY", "SELL", "SELL"]
    return create_graph(mapped_neighbors, mapped_roles)

def test_graph2():
    mapped_neighbors = [[1], [2], [1]]
    mapped_roles = ["BUY", "SELL", "BUY"]
    return create_graph(mapped_neighbors, mapped_roles)

def test_graph3():
    mapped_neighbors = [[1], [2], [1], [1]]
    mapped_roles = ["BUY", "SELL", "BUY", "BUY"]
    return create_graph(mapped_neighbors, mapped_roles)

def test_graph4():
    mapped_neighbors = [[1], [2], [1], [1], [1]]
    mapped_roles = ["BUY", "SELL", "BUY", "BUY", "BUY"]
    return create_graph(mapped_neighbors, mapped_roles)

def test_graph5():
    mapped_neighbors = [[1], [0]]
    mapped_roles = ["BUY", "SELL"]
    return create_graph(mapped_neighbors, mapped_roles)

def test_graph6():
    mapped_neighbors = [[1], [2], [1], [1], [1], [1]]
    mapped_roles = ["BUY", "SELL", "BUY", "BUY", "BUY", "BUY"]
    return create_graph(mapped_neighbors, mapped_roles)