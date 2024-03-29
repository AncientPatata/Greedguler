import networkx as nx
import matplotlib.pyplot as plt
import datetime

import algorithm as alg
from data_loader import load_dag_from_json


def transform_node_to_edge(G):
    """
    Transforms a graph by converting node weights into edge weights.
    
    Each node's weight in the input graph is applied as the weight of outgoing edges. Additionally,
    a special 'end' node is created, and all leaf nodes are connected to this 'end' node with their weights.
    
    Parameters:
    - G (nx.DiGraph): The input directed acyclic graph (DAG) with nodes having 'duration' as their weight.
    
    Returns:
    - nx.DiGraph: A transformed directed graph with node weights converted to edge weights.
    """
    Gt = nx.DiGraph()

    Gt.add_nodes_from(list(G.nodes()))
    for parent, child in list(G.edges()):
        parent_weight = G.nodes[parent]['duration']
        Gt.add_edge(parent, child, weight=parent_weight)
   
    feuilles = [node for node in G.nodes() if len(nx.descendants(G, node)) == 0]
    Gt.add_node('end')

    for feuille in feuilles:
        Gt.add_edge(feuille, 'end')
        Gt[feuille]['end']['weight'] = G.nodes[feuille]['duration']

    return Gt



def total_weight(T):
    """
    Calculates the total weight of all edges in a graph.
    
    Parameters:
    - T (nx.DiGraph): The directed graph whose edge weights are to be summed.
    
    Returns:
    - datetime.timedelta: The sum of all edge weights in the graph.
    """
    somme_timedelta = datetime.timedelta()
    for (u, v) in T.edges():
        somme_timedelta += T[u][v]['weight']
    return somme_timedelta


def critical_path(G):
    """
    Finds the critical path in the input graph, defined as the longest path in terms of total duration.
    
    Parameters:
    - G (nx.DiGraph): The directed acyclic graph (DAG) in which to find the critical path.
    
    Returns:
    - datetime.timedelta: The total duration of the critical path.
    """
    T = transform_node_to_edge(G)
    critical_path_length = datetime.timedelta()
    critical_path = nx.dag_longest_path(Gt, weight='duration')
    for (u, v) in T.edges():
        if u in critical_path and v in critical_path:
            critical_path_length += T[u][v]['weight']
    return critical_path_length


def makespan(G, nombre_machine):
    """
    Calculates the makespan for a given graph and number of machines, using a heuristic allocation algorithm.
    
    Parameters:
    - G (nx.DiGraph): The input graph representing jobs to be scheduled.
    - nombre_machine (int): The number of machines available for scheduling.
    
    Returns:
    - datetime.timedelta: The makespan for the scheduling scenario.
    """
    A = G.copy()
    schedule = alg.allocate_jobs_to_machines_with_heuristic(A ,num_machines=nombre_machine)
    pers_makespan = []
    for machine in schedule:
        pers_makespan.append(machine[-1]['end_time'])
    makespan = max(pers_makespan)
    return makespan


def convertir_date(secondes):
    """
    Converts a duration in seconds into a more readable format (days, hours, minutes, seconds).
    
    Parameters:
    - secondes (int): The duration in seconds.
    
    Returns:
    - datetime.timedelta: The duration as a datetime.timedelta object.
    """
    jours = secondes // (24 * 3600)
    secondes_restantes = secondes % (24 * 3600)
    heures = secondes_restantes // 3600
    secondes_restantes %= 3600
    minutes = secondes_restantes // 60
    secondes_restantes %= 60
    duree = datetime.timedelta(days=jours, hours=heures, minutes=minutes, seconds=secondes)
    return duree


def SLR(G, nombre_machine):
    """
    Calculates the Schedule Length Ratio (SLR) for a graph and a given number of machines.
    
    The SLR is the ratio of the makespan to the total duration of the critical path, indicating efficiency.
    
    Parameters:
    - G (nx.DiGraph): The graph representing the set of jobs.
    - nombre_machine (int): The number of machines over which jobs are to be scheduled.
    
    Returns:
    - float: The Schedule Length Ratio.
    """
    MSP = makespan(G, nombre_machine)
    crit_path = critical_path(G).total_seconds()
    return MSP / crit_path


if __name__ == "__main__":
    G = load_dag_from_json("./smallComplex.json")
    Gt = transform_node_to_edge(G)
    print("Le poids total est", total_weight(Gt))
    print("Le poids du chemin critique est", critical_path(G))
    MSP = makespan(G, 3)
    print("Le makespan est de", convertir_date(makespan(G, 1500)))
    print("Le SLR est de", SLR(G, 3))




