import plotly.express as px
import plotly.figure_factory as ff
import json 
import pandas as pd
from datetime import datetime, timedelta
import argparse

import dash
from dash import dcc
import dash_cytoscape as cyto
from dash import html

import algorithm
import data_loader
import verification
from data_loader import load_dag_from_json
import os


#from networkx.drawing.nx_pydot import graphviz_layout # TODO: If condition to check if graphviz is installed
import networkx as nx

cyto.load_extra_layouts()

def plot_schedule(schedule,file_input=True, output='html'): # TODO: remove second argument
    if file_input:
        with open(schedule) as file_handle:
            schedule = json.load(file_handle)
    job_list = [] 
    for (index, machine_jobs) in enumerate(schedule):
        machine = "Machine " + str(index+1)
        job_list += [{"job_index": job["job_index"],"start_time": datetime.fromtimestamp(job["start_time"]), "end_time": datetime.fromtimestamp(job["end_time"]), "duration": job["duration"], "machine": machine} for job in machine_jobs] #[dict(job, **{"machine": machine}) for job in machine_jobs[:10] ]

    df = pd.DataFrame(job_list)
    
    fig_sched = px.timeline(df, x_start="start_time", x_end="end_time", y="machine", color="machine", hover_data="job_index")
    if output != "Dash":
        return fig_sched.to_html(full_html=False, include_plotlyjs='cdn')
    else:
        return fig_sched 
            
        

def elements_from_nx(graph):
    #pos =  graphviz_layout(graph, prog="dot")
    elements = []
    
    for node in graph.nodes:
        elements.append({'data': {'id': str(node), 'label': str(node) }})
    for edge in graph.edges:
        elements.append({'data': {'source': str(edge[0]), 'target': str(edge[1]), 'duration': str(nx.get_node_attributes(graph, 'duration')[edge[0]])}})
    return elements
        


# Specify the file name for the graph
GRAPH_FILE = './intermediates/test_graph.graphml'


def calculate_schedule(dag: nx.DiGraph, num_machines, calculate_criteria = True) -> list:
    dag_sc1 = dag.copy()
    dag_sc2 = dag.copy()
    schedule_1 = algorithm.heft(dag_sc1 ,num_machines=num_machines)
    with open("intermediates/schedule_1.json", "w") as file_handle:
        json.dump(schedule_1, file_handle)
    schedule_2 = algorithm.allocate_jobs_to_machines_nx(dag_sc2 ,num_machines=num_machines)
    with open("intermediates/schedule_2.json", "w") as file_handle:
        json.dump(schedule_2, file_handle)
    overlap_schedule_1 = verification.verifcation_overlap_machine(schedule_1)
    dependencies_schedule_1 = verification.verification_dependencies(dag, schedule_1)
    overlap_schedule_2 = verification.verifcation_overlap_machine(schedule_2)
    dependencies_schedule_2 = verification.verification_dependencies(dag, schedule_2)
    result = [{'schedule': schedule_1, 'overlap': overlap_schedule_1, 'dependencies': dependencies_schedule_1},
              {'schedule': schedule_2, 'overlap': overlap_schedule_2, 'dependencies': dependencies_schedule_2}]
    if calculate_criteria:
        critical_path_duration:timedelta = timedelta(seconds=0)
        critical_path = nx.dag_longest_path(dag)
        for node in critical_path:
            critical_path_duration += nx.get_node_attributes(dag,"duration")[node]
        srs_1 = max([l[-1]["end_time"] for l in schedule_1]) / critical_path_duration.total_seconds()
        srs_2 = max([l[-1]["end_time"] for l in schedule_2]) / critical_path_duration.total_seconds()
        result[0]["srs"] = srs_1
        result[1]["srs"] = srs_2
        result[0]["critical_path_duration"] = critical_path_duration
        result[1]["critical_path_duration"] = critical_path_duration
        return result
    else:
        return result


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



if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog="data_viz")
    parser.add_argument('num_machines', type=int, help='Number of machines', default=3)
    parser.add_argument("--schedule_only", type=str, nargs="+", help="List of paths to the schedule json files that you want to visualize")
    parser.add_argument('--file', help='Path to the file containing the DAG (optional)')
    parser.add_argument('--gen', action='store_true', help='Generate a random DAG (optional)')
    parser.add_argument('--num_nodes', type=int, help='Number of nodes in the DAG (required if --gen is used)')
    parser.add_argument('--max_duration', type=int, help='Maximum duration of jobs in the DAG (required if --gen is used)')
    parser.add_argument('--density', type=int, help="Set the edge density for the generated graph ", default=1)
    parser.add_argument("--reload", action="store_true", help="Reuse previously generated graph and regenerate a schedule again")
    parser.add_argument("--nograph", action="store_true", help="Use if you don't want to render a large graph, must be used for larger data")
    args = parser.parse_args()
    app_contents = []
    if args.schedule_only:
        # Load schedule from file and append it to the page to draw
        for file in args.schedule_only:
            app_contents.append(dcc.Graph(figure=plot_schedule(file, output="Dash")))
        
    elif args.file:
        dag = data_loader.load_dag_from_json(args.file)
        schedules = calculate_schedule(dag, args.num_machines)
        app_contents.append(html.Div("Critical Path Length : " + str(schedules[0]["critical_path_duration"])))
        for schedule in schedules:
            app_contents.append(dcc.Graph(figure=plot_schedule(schedule["schedule"],file_input=False, output="Dash")))
            app_contents.append(html.Div("SRS = " + str(schedule["srs"])))
            app_contents.append(html.Div("Overlap = " + str(schedule["overlap"])))
            app_contents.append(html.Div("Dependencies = " + str(schedule["dependencies"])))
            
        pass 
    elif args.gen:
        if not (args.num_nodes and args.max_duration):
            parser.error("--gen requires --num_nodes and --max_duration.")
        # Generate a new random DAG
        dag = data_loader.generate_random_dag(args.num_nodes, args.max_duration, density_level=args.density)
        # Convert timedelta values to total seconds for 'duration' attribute
        cached_dag = dag.copy()
        for node, data in cached_dag.nodes(data=True):
            if 'duration' in data:
                data['duration'] = data['duration'].total_seconds()
        # Save the generated graph to the file
        nx.write_graphml(cached_dag, GRAPH_FILE)
        print("New graph generated and saved to file.")
        # RECALCULATE SCHEDULE
        schedules = calculate_schedule(dag, args.num_machines)
        app_contents.append(html.Div("Critical Path Length : " + str(schedules[0]["critical_path_duration"])))
        for schedule in schedules:
            app_contents.append(dcc.Graph(figure=plot_schedule(schedule["schedule"],file_input=False, output="Dash")))
            app_contents.append(html.Div("SRS = " + str(schedule["srs"])))
            app_contents.append(html.Div("Overlap = " + str(schedule["overlap"])))
            app_contents.append(html.Div("Dependencies = " + str(schedule["dependencies"])))
            
    elif args["reload"]:
        # Load the existing graph
        dag = nx.read_graphml(GRAPH_FILE)
        # Convert total seconds back to timedelta for 'duration' attribute
        for node, data in dag.nodes(data=True):
            if 'duration' in data:
                data['duration'] = timedelta(seconds=data['duration'])
        print("Graph loaded from file.") 
        # RECALCULATE SCHEDULE
        schedules = calculate_schedule(dag, args.num_machines)
        app_contents.append(html.Div("Critical Path Length : " + str(schedules[0]["critical_path_duration"])))
        for schedule in schedules:
            app_contents.append(dcc.Graph(figure=plot_schedule(schedule["schedule"],file_input=False, output="Dash")))
            app_contents.append(html.Div("SRS = " + str(schedule["srs"])))
            app_contents.append(html.Div("Overlap = " + str(schedule["overlap"])))
            app_contents.append(html.Div("Dependencies = " + str(schedule["dependencies"])))

    else: 
        parser.error("You have to provide one of the four available options : --file, --gen, --reload or --schedule_only ")
    
    if not (args.schedule_only or args.nograph):
        app_contents.append(cyto.Cytoscape(
        id="cytoscape",
        elements=elements_from_nx(dag),
        style={'width': '100%', 'height': '700px'},
        layout={
                'name': 'dagre', 
                'rankSep': 20, 
                'edgeSep': 10,
                'nodeSep': 10, 
                'spacingFactor': 1.2
            },
            responsive=True,
          stylesheet=default_stylesheet
        ))
        
        @app.callback(
            dash.Output('cytoscape', 'stylesheet'),
            dash.Input('cytoscape', 'tapNodeData'),
        )
        def highlight_neighbors(selected_node):
            if not selected_node:
                return default_stylesheet

            selected_node_id = str(selected_node['id'])
            highlighted_nodes = set([selected_node_id])
            highlighted_edges = []

            for edge in dag.edges:
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
    

    app.layout = html.Div(app_contents)
    app.run_server(debug=True)
