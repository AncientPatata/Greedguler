import networkx as nx
import random
import matplotlib.pyplot as plt

# Création du graphe vide
T = nx.DiGraph()

# Définition des noeuds
nodes = ['A', 'B', 'C', 'D', 'E', 'F', 'G']
num_nodes = len(nodes)

# Computer la somme des temps d'exécution de toutes les tâches afin de vérifier que le résultat obtenu n'est pas absurde.
# En effet, si le makespan est plus grand que cette somme (équivalent à run toutes les tâches sur un seul noeud) le résultat est incorrect
total_weight = 0

# Ajouter les nœuds avec des poids aléatoires entre 1 et 10
for node in nodes:
    weight = random.randint(1, 10)
    T.add_node(node, weight=weight)
    total_weight += weight

print("Le temps total d'exécution est de", total_weight)

# Création des arêtes du graphe
# Transformation du graphe où les poids sont sur les noeuds en un graphe où les poids sont sur les arêtes
# Nous effectuons cette transformation car la fonction nx.dag_longest_path prend en compte le poids des arêtes mais pas le poids des sommets
T.add_node('end')

T.add_edge('A', 'B')
T['A']['B']['poids'] = T.nodes['A']['weight']

T.add_edge('A', 'D')
T['A']['D']['poids'] = T.nodes['A']['weight']

T.add_edge('B', 'C')
T['B']['C']['poids'] = T.nodes['B']['weight']

T.add_edge('B', 'E')
T['B']['E']['poids'] = T.nodes['B']['weight']

T.add_edge('D', 'E')
T['D']['E']['poids'] = T.nodes['D']['weight']

T.add_edge('C', 'F')
T['C']['F']['poids'] = T.nodes['C']['weight']

T.add_edge('E', 'F')
T['E']['F']['poids'] = T.nodes['E']['weight']

T.add_edge('F', 'G')
T['F']['G']['poids'] = T.nodes['F']['weight']

T.add_edge('G', 'end')
T['G']['end']['poids'] = T.nodes['G']['weight']

# Calcul du chemin le plus long, ce paramètre nous sera utile pour le calcul du SLR
print(nx.dag_longest_path(T, weight='poids'))

def SLR(T):
    # En pratique le makespan est calculé avec l'algorithme que l'on va développer en utlisant la fonction time.timeit()
    makespan = nx.dag_longest_path_length(T, weight='poids') 
    return makespan / nx.dag_longest_path_length(T, weight='poids')

def one_node(T):
    return T.size(weight='poids')

print(one_node(T))

# Dessiner le graphe avec des poids de noeuds
pos = nx.spring_layout(T)  # Positions des noeuds pour un dessin compréhensible
edge_labels = {(u, v): d['poids'] for u, v, d in T.edges(data=True)}  # Création des étiquettes d'arêtes
nx.draw(T, pos, with_labels=True, node_size=2000, node_color='skyblue', font_size=12, font_weight='bold')
nx.draw_networkx_edge_labels(T, pos, edge_labels=edge_labels, font_color='red', font_size=10)  # Affichage des poids d'arêtes

# Afficher le graphe
plt.title("Graphe avec des poids de noeuds aléatoires entre 1 et 10")
plt.show()



