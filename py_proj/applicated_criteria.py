import networkx as nx
import matplotlib.pyplot as plt
import datetime

import algorithm as alg
from data_loader import load_dag_from_json


G = load_dag_from_json("./smallComplex.json")


def transform_node_to_edge(G):
    Gt = nx.DiGraph()

    Gt.add_nodes_from(list(G.nodes()))
    # Ajoutez les arêtes avec les poids des nœuds parents
    for parent, child in list(G.edges()):
        parent_weight = G.nodes[parent]['duration']
        Gt.add_edge(parent, child, weight=parent_weight)
   
    # On rejoint toutes les feuilles avec le noeud 'end', chacune de ces arêtes aura pour poids le poids du noeud parent/ de la feuille
    feuilles = [node for node in G.nodes() if len(nx.descendants(G, node)) == 0]
    Gt.add_node('end')

    for feuille in feuilles:
        Gt.add_edge(feuille, 'end')
        Gt[feuille]['end']['weight'] = G.nodes[feuille]['duration']

    return Gt

Gt = transform_node_to_edge(G)


def total_weight(T):
    somme_timedelta = datetime.timedelta()
    # Ajouter chaque timedelta à la somme
    for (u, v) in T.edges():
        somme_timedelta += T[u][v]['weight']
    return somme_timedelta

print("Le poids total est", total_weight(Gt))


def critical_path(G):
    T = transform_node_to_edge(G)
    critical_path_length = datetime.timedelta()
    critical_path = nx.dag_longest_path(Gt, weight='duration')
    for (u, v) in T.edges():
        if u in critical_path and v in critical_path:
            critical_path_length += T[u][v]['weight']
    return critical_path_length

print("Le poids du chemin critique est", critical_path(G))


def makespan(G, nombre_machine):
    A = G.copy()
    schedule = alg.allocate_jobs_to_machines_with_heuristic(A ,num_machines=nombre_machine)
    pers_makespan = []
    for machine in schedule:
        pers_makespan.append(machine[-1]['end_time'])
    makespan = max(pers_makespan)
    return makespan

MSP = makespan(G, 3)

def convertir_date(secondes):
    jours = secondes // (24 * 3600)
    secondes_restantes = secondes % (24 * 3600)
    heures = secondes_restantes // 3600
    secondes_restantes %= 3600
    minutes = secondes_restantes // 60
    secondes_restantes %= 60
    duree = datetime.timedelta(days=jours, hours=heures, minutes=minutes, seconds=secondes)
    return duree

print("Le makespan est de", convertir_date(makespan(G, 1500)))


def critical_path(Gt):
    longest_path = nx.dag_longest_path(Gt, weight='duration')
    crit_length = datetime.timedelta()
    for node in longest_path:
        crit_length += Gt.nodes[node]['duration']
    return crit_length


def SLR(G, nombre_machine):
    MSP = makespan(G, nombre_machine)
    crit_path = critical_path(G).total_seconds()
    return MSP / crit_path

print("Le SLR est de", SLR(G, 3))




