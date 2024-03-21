import networkx as nx
import matplotlib.pyplot as plt
from networkx.drawing.nx_pydot import graphviz_layout
import rustworkx as rx
import random
import json
#import orjson as json
from datetime import datetime, timedelta
import timeit

def generate_random_dag(num_nodes, max_duration, density_level=2):
    # Create a directed acyclic graph (DAG)
    dag = nx.DiGraph()

    # Add nodes to the graph
    for i in range(num_nodes):
        dag.add_node(i, duration=timedelta(seconds=random.randint(1, max_duration)))

    # Add edges to create a DAG
    for i in range(num_nodes - 1):
        for j in range(i + 1, num_nodes):
            if random.choice([True] + [False]*density_level):
                dag.add_edge(i, j)

    return dag

def plot_dag(dag):
    pos =  graphviz_layout(dag, prog="dot")
    #durations = {node: dag.nodes[node]['duration'] for node in dag.nodes}

    nx.draw(dag, pos, with_labels=False, node_size=8, node_color='skyblue')
    #nx.draw_networkx_edge_labels(dag, pos, edge_labels={(i, j): f"{durations[i]} units" for i, j in dag.edges})

    plt.title("DAG with Random Durations")
    #plt.savefig("dag.png")
    plt.show()
@profile
def load_dag_from_json(filepath):
    print("Loading DAG from JSON file " + filepath + "....") #TODO: Custom logging with control of verbosity.
    start_time = timeit.default_timer()
    graph = nx.DiGraph()
    with open(filepath, "r") as file_handle:
        object_data = json.load(file_handle)
        nodes:dict = object_data["nodes"]
        #node_indices = [(int(k), {"duration":datetime.strptime(v["Data"][:-1], "%H:%M:%S.%f")} ) for (k,v) in nodes.items()]
        node_indices = [(int(k), {"duration":timedelta(hours=int(time_parts[0]), minutes=int(time_parts[1]), seconds=float(time_parts[2]))} ) for (k,v) in nodes.items() if (time_parts:=v["Data"].split(':'))]
        edges = []
        for (k,v) in nodes.items():
            for dep in v["Dependencies"]:
                edges.append((dep, int(k)))
        graph.add_nodes_from(node_indices)
        graph.add_edges_from(edges)
    elapsed = timeit.default_timer() - start_time
    print("Loading file took : ", elapsed) # TODO: timeit for JSON file loading
    
    return graph

@profile
def load_dag_from_json_aug(filepath):
    print("Loading DAG from JSON file " + filepath + "....") #TODO: Custom logging with control of verbosity.
    start_time = timeit.default_timer()
    graph = nx.DiGraph()
    object_data = rs.parse_json_graph(filepath)
    nodes = object_data["nodes"]
    #node_indices = [(int(k), {"duration":datetime.strptime(v["Data"][:-1], "%H:%M:%S.%f")} ) for (k,v) in nodes.items()]
    node_indices = [(int(k), {"duration":timedelta(hours=int(time_parts[0]), minutes=int(time_parts[1]), seconds=float(time_parts[2]))} ) for (k,v) in nodes.items() if (time_parts:=v["data"].split(':'))]
    edges = []
    for (k,v) in nodes.items():
        for dep in v["dependencies"]:
            edges.append((dep, int(k)))
    graph.add_nodes_from(node_indices)
    graph.add_edges_from(edges)
    elapsed = timeit.default_timer() - start_time
    print("Loading file took : ", elapsed) # TODO: timeit for JSON file loading
    
    return graph
        
@profile    
def load_dag_from_json_rx(filepath):
    print("Loading DAG from JSON file " + filepath + "....")  # TODO: Custom logging with control of verbosity.
    start_time = timeit.default_timer()
    graph = rx.PyDiGraph()
    durations = {}
    nodes_list = []
    edges_list = []
    with open(filepath, "r") as file_handle:
        object_data = json.load(file_handle)
        nodes = object_data["nodes"]
        for node_id, node_data in nodes.items():
            time_parts = node_data["Data"].split(':')
            duration = timedelta(hours=int(time_parts[0]), minutes=int(time_parts[1]), seconds=float(time_parts[2]))
            durations[int(node_id)] = duration  # Storing duration in the durations dictionary
            nodes_list.append(int(node_id))
            edges_list += [(dep, int(node_id)) for dep in node_data["Dependencies"]]
    del object_data
    node_indices = graph.add_nodes_from(nodes_list)
    mapping = dict(zip(nodes_list, node_indices))
    del nodes_list
    del node_indices
    new_edges_list = [(mapping[a], mapping[b]) for a, b in edges_list]
    del edges_list
    graph.add_edges_from_no_data(new_edges_list)
    del new_edges_list
    elapsed = timeit.default_timer() - start_time
    print("Loading file took:", elapsed)  # TODO: timeit for JSON file loading

    return graph, durations

@profile    
def load_dag_from_json_rx_aug(filepath):
    print("Loading DAG from JSON file " + filepath + "....")  # TODO: Custom logging with control of verbosity.
    start_time = timeit.default_timer()
    graph = rx.PyDiGraph()
    durations = {}
    nodes_list = []
    edges_list = []
    object_data = rs.parse_json_graph(filepath)
    nodes = object_data["nodes"]
    for node_id, node_data in nodes.items():
        time_parts = node_data["data"].split(':')
        duration = timedelta(hours=int(time_parts[0]), minutes=int(time_parts[1]), seconds=float(time_parts[2]))
        durations[int(node_id)] = duration  # Storing duration in the durations dictionary
        nodes_list.append(int(node_id))
        for dep in node_data["dependencies"]:
            edges_list.append((dep, int(node_id)))
    node_indices = graph.add_nodes_from(nodes_list)
    mapping = dict(zip(nodes_list, node_indices))
    edges_list = list(map(lambda x: (mapping[x[0]], mapping[x[1]]), edges_list))
    graph.add_edges_from_no_data(edges_list)
    elapsed = timeit.default_timer() - start_time
    print("Loading file took:", elapsed)  # TODO: timeit for JSON file loading

    return graph, durations

import rapid_scheduler as rs


if __name__ == "__main__":

    #dag = generate_random_dag(num_nodes, max_duration)
    # dag = load_dag_from_json_rx_aug("./data/xlargeComplex.json")
    # del dag
    # dag = load_dag_from_json_aug("./data/MediumComplex.json")
    dag = load_dag_from_json_rx("./data/MediumComplex.json")
    del dag
    

    # start_time = timeit.default_timer()
    # graph = rs.parse_json_graph("./data/xlargeComplex.json")
    # elapsed = timeit.default_timer() - start_time
    # print(graph)
    # print("Loading file took:", elapsed)  # TODO: timeit for JSON file loading
    
    # start_time = timeit.default_timer()
    # with open("./data/xlargeComplex.json", "r") as file_handle:
    #     object_data = json.load(file_handle)
    # elapsed = timeit.default_timer() - start_time
    # del object_data 
    # print("Loading file took:", elapsed)  # TODO: timeit for JSON file loading
    # print(nx.get_node_attributes(dag,"duration"))
    #plot_dag(dag)