# Import necessary libraries
import networkx as nx
import matplotlib.pyplot as plt
from networkx.drawing.nx_pydot import graphviz_layout
import random
import json
from datetime import datetime, timedelta
import timeit
import rustworkx as rx


def generate_random_dag(num_nodes:int, max_duration:int, density_level=2):
    """
    Generates a random Directed Acyclic Graph (DAG) with specified number of nodes,
    maximum duration for each node, and density level for edge creation.

    :param num_nodes: The number of nodes in the DAG.
    :type num_nodes: int
    :param max_duration: The maximum duration of each node as a limit for random generation.
    :type max_duration: int
    :param density_level: Controls the density of edges in the DAG. Higher values result in a sparser graph. Defaults to 2.
    :type density_level: int, optional
    :return: A networkx DiGraph object representing the generated DAG.
    :rtype: nx.DiGraph
    """
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
    """
    Plots a Directed Acyclic Graph (DAG) using graphviz layout and networkx drawing tools.

    :param dag: The directed acyclic graph to plot.
    :type dag: nx.DiGraph
    :return: This function displays the plot but does not return any value.
    :rtype: None
    """
    pos =  graphviz_layout(dag, prog="dot")

    nx.draw(dag, pos, with_labels=False, node_size=8, node_color='skyblue')

    plt.title("DAG with Random Durations")
    plt.show()


def load_dag_from_json(filepath: str):
    """
    Loads a DAG from a JSON file. The JSON format is expected to contain nodes with durations and their dependencies.

    :param filepath: The path to the JSON file containing the DAG information.
    :type filepath: str
    :return: A networkx DiGraph object representing the loaded DAG.
    :rtype: nx.DiGraph
    """
    print("Loading DAG from JSON file " + filepath + "....") #TODO: Custom logging with control of verbosity.
    start_time = timeit.default_timer()
    graph = nx.DiGraph()
    with open(filepath, "r") as file_handle:
        object_data = json.load(file_handle)
        nodes:dict = object_data["nodes"]
        node_indices = [(int(k), {"duration":timedelta(hours=int(time_parts[0]), minutes=int(time_parts[1]), seconds=float(time_parts[2]))} ) for (k,v) in nodes.items() if (time_parts:=v["Data"].split(':'))]
        edges = []
        for (k,v) in nodes.items():
            for dep in v["Dependencies"]:
                edges.append((dep, int(k)))
        graph.add_nodes_from(node_indices)
        graph.add_edges_from(edges)
    elapsed = timeit.default_timer() - start_time
    print("Loading file took : ", elapsed)
    return graph
        
#@profile    
def load_dag_from_json_rx(filepath):
    """
    Loads a DAG from a JSON file into a retworkx PyDiGraph and a durations dictionary, tailored for high performance.

    :param filepath: The path to the JSON file containing the DAG information.
    :type filepath: str
    :return: A tuple containing the retworkx PyDiGraph and a dictionary mapping node IDs to their durations.
    :rtype: tuple
    """
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
            durations[int(node_id)] = duration
            nodes_list.append(int(node_id))
            edges_list += [(dep, int(node_id)) for dep in node_data["Dependencies"]]
    del object_data
    node_indices = graph.add_nodes_from(nodes_list)
    mapping = dict(zip(nodes_list, node_indices))
    del nodes_list # Explicit deletion (outside of Python's garbage collection) probably takes more time overall but it helps reduce memory usage
    del node_indices
    new_edges_list = [(mapping[a], mapping[b]) for a, b in edges_list]
    del edges_list
    graph.add_edges_from_no_data(new_edges_list)
    del new_edges_list
    elapsed = timeit.default_timer() - start_time
    print("Loading file took:", elapsed)
    return graph, durations

if __name__ == "__main__":
    # Example usage of the functions defined above
    # Uncomment the desired function calls to generate, load, and plot a DAG
    # dag = generate_random_dag(num_nodes, max_duration)
    # dag = load_dag_from_json("./smallComplex.json")
    # print(nx.get_node_attributes(dag,"duration"))
    # plot_dag(dag)
    print("Please run the greedguler or data_viz files instead.")