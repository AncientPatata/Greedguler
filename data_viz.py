import plotly.express as px
import plotly.figure_factory as ff
import json 
import pandas as pd
from datetime import datetime
import igviz

import dash
from dash import dcc
import dash_cytoscape as cyto
from dash import html

import algorithm
import data_loader
from data_loader import load_dag_from_json
#from networkx.drawing.nx_pydot import graphviz_layout # TODO: If condition to check if graphviz is installed
import networkx as nx

cyto.load_extra_layouts()

def plot_schedule(schedule_file, output='html'): # TODO: remove second argument
    df = pd.DataFrame()
    with open("schedule.json") as file_handle:
        schedule = json.load(file_handle)
        job_list = [] #[{"start_time": 0, "end_time": 5.3, "machine": 1},{"start_time": 1.05, "end_time": 3, "machine": 2}]
        for (index, machine_jobs) in enumerate(schedule):
            machine = "Machine " + str(index+1)
            job_list += [{"job_index": job["job_index"],"start_time": datetime.fromtimestamp(job["start_time"]), "end_time": datetime.fromtimestamp(job["end_time"]), "duration": job["duration"], "machine": machine} for job in machine_jobs] #[dict(job, **{"machine": machine}) for job in machine_jobs[:10] ]
            
        df = pd.DataFrame(job_list)
    
    fig_sched = px.timeline(df, x_start="start_time", x_end="end_time", y="machine", color="machine", hover_data="job_index")
    if output != "Dash":
        return fig_sched.to_html(full_html=False, include_plotlyjs='cdn')
    else:
        return fig_sched 
            
        
        

def plot_graph_to_html(dag):
    fig_graph = igviz.plot(dag, layout="planar", node_label="job_index", node_text=["duration"])
    # TODO: Look for a way to make use of GraphViz layout
    return fig_graph.to_html(full_html=False, include_plotlyjs='cdn')
    
def elements_from_nx(graph):
    #pos =  graphviz_layout(graph, prog="dot")
    elements = []
    
    for node in graph.nodes:
        elements.append({'data': {'id': str(node), 'label': str(node) }})
    for edge in graph.edges:
        elements.append({'data': {'source': str(edge[0]), 'target': str(edge[1]), 'duration': str(nx.get_node_attributes(graph, 'duration')[edge[0]]) + ' s'}})
    return elements
        

dag = data_loader.generate_random_dag(12,86)
plotting_dag = dag.copy()
schedule = algorithm.allocate_jobs_to_machines_mod(dag ,num_machines=3)
#print(schedule)
with open("schedule.json", "w") as file_handle:
    json.dump(schedule, file_handle)

default_stylesheet =  [
        {
            "selector": 'node',
            "style": {
                'content': 'data(id)',
                'label': 'data(label)'
            }
        },
        {
            "selector": 'edge',
            "style": {
                'label': 'data(duration)',
                'curve-style':'straight',
                'line-color': '#ccc',
                'target-arrow-color': '#ccc',
                'target-arrow-shape': 'triangle'
            }
        },
    ]

app = dash.Dash(__name__)
app.layout = html.Div([
    dcc.Graph(figure=plot_schedule("schedule.json", output="Dash")),
    cyto.Cytoscape(
        id="cytoscape",
        elements=elements_from_nx(plotting_dag),
        layout={
                'name': 'dagre'
            },
            responsive=True,
          stylesheet=default_stylesheet
    ),
])


@app.callback(
    dash.Output('cytoscape', 'stylesheet'),
    dash.Input('cytoscape', 'tapNodeData')
)
def highlight_neighbors(selected_node):
    if not selected_node:
        return default_stylesheet

    selected_node_id = str(selected_node['id'])
    highlighted_nodes = set([selected_node_id])
    highlighted_edges = []

    for edge in plotting_dag.edges:
        if selected_node_id == str(edge[1]):
            highlighted_nodes.add(str(edge[0]))
            highlighted_nodes.add(str(edge[1]))
            highlighted_edges.append({'selector': f'edge[source="{edge[0]}"][target="{edge[1]}"]', 'style': {'line-color': '#78D5D7'}})
        elif selected_node_id == str(edge[0]):
            highlighted_edges.append({'selector': f'edge[source="{edge[0]}"][target="{edge[1]}"]', 'style': {'line-color': '#C21F3D'}})


    stylesheet = [
        {
            "selector": 'node',
            "style": {
                'content': 'data(id)',
                'label': 'data(label)'
            }
        },
        {
            "selector": 'edge',
            "style": {
                'label': 'data(duration)',
                'curve-style': 'straight',
                'line-color': '#ccc',
                'target-arrow-color': '#ccc',
                'target-arrow-shape': 'triangle'
            }
        },
    ]

    for node_id in highlighted_nodes:
        stylesheet.append({'selector': f'node[id="{node_id}"]', 'style': {'background-color': '#2081C3'}})

    return stylesheet + highlighted_edges


if __name__ == "__main__":
    
    # with open('schedule_viz.html', 'a') as f:
    #     f.write(plot_schedule_to_html("schedule.json"))
    app.run_server(debug=True)
