# Import necessary libraries
import networkx as nx
import matplotlib.pyplot as plt
from networkx.drawing.nx_pydot import graphviz_layout
import random
import json
from datetime import datetime, timedelta
import timeit
import rustworkx as rx

def generate_random_dag(num_nodes, max_duration, density_level=2):
    '''
    Generates a random directed acyclic graph (DAG).

    Args:
        num_nodes (int): Number of nodes in the DAG.
        max_duration (int): Maximum duration for node execution.
        density_level (int, optional): Density level for adding edges. Defaults to 2.

    Returns:
        nx.DiGraph: Randomly generated DAG.
    '''
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
    '''
    Plots the given DAG.

    Args:
        dag (nx.DiGraph): Directed acyclic graph.
    '''
    pos =  graphviz_layout(dag, prog="dot")
    nx.draw(dag, pos, with_labels=False, node_size=8, node_color='skyblue')
    plt.title("DAG with Random Durations")
    plt.show()

def load_dag_from_json(filepath):
    '''
    Loads a DAG from a JSON file.

    Args:
        filepath (str): Path to the JSON file.

    Returns:
        nx.DiGraph: Directed acyclic graph loaded from JSON data.
    '''
    print("Loading DAG from JSON file " + filepath + "....")
    start_time = timeit.default_timer()
    graph = nx.DiGraph()
    with open(filepath, "r") as file_handle:
        object_data = json.load(file_handle)
        nodes = object_data["nodes"]
        node_indices = [(int(k), {"duration": timedelta(hours=int(v["Data"].split(':')[0]), 
                                                      minutes=int(v["Data"].split(':')[1]), 
                                                      seconds=float(v["Data"].split(':')[2]))}) 
                        for k, v in nodes.items() if ":" in v["Data"]]
        edges = [(dep, int(k)) for k, v in nodes.items() for dep in v["Dependencies"]]
        graph.add_nodes_from(node_indices)
        graph.add_edges_from(edges)
    elapsed = timeit.default_timer() - start_time
    print("Loading file took : ", elapsed)
    return graph

@profile    
def load_dag_from_json_rx(filepath):
    '''
    Loads a DAG from a JSON file using rustworkx.

    Args:
        filepath (str): Path to the JSON file.

    Returns:
        rustworkx.PyDiGraph: Directed acyclic graph loaded from JSON data.
        dict: Durations of nodes in the graph.
    '''
    print("Loading DAG from JSON file " + filepath + "....")
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
            durations[int(node_id)] = duration
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
    print("Loading file took:", elapsed)
    return graph, durations

if __name__ == "__main__":
    # Example usage
    num_nodes = 7
    max_duration = 5

    # Load a DAG from a JSON file
    dag = load_dag_from_json("./smallComplex.json")
