import networkx as nx
import matplotlib.pyplot as plt
from networkx.drawing.nx_pydot import graphviz_layout
import random
import json
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
        

if __name__ == "__main__":

    # Example usage
    num_nodes = 7
    max_duration = 5

    #dag = generate_random_dag(num_nodes, max_duration)
    dag = load_dag_from_json("./smallComplex.json")
    # print(nx.get_node_attributes(dag,"duration"))
    #plot_dag(dag)