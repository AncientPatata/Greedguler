import networkx as nx
from datetime import datetime, timedelta
import rustworkx as rx
from copy import deepcopy

def allocate_jobs_to_machines(job_durations, num_machines):
    # Initialize machines as empty lists
    machines = [[] for _ in range(num_machines)]

    # Sort job durations in descending order
    sorted_jobs = enumerate(job_durations) #sorted(enumerate(job_durations), key=lambda x: x[1], reverse=True)

    # Greedy allocation
    for job_index, duration in sorted_jobs:
        # Find the machine with the earliest end time
        min_end_time_machine = min(machines, key=lambda machine: (machine[-1]['end_time'] if machine else 0))
        max_end_time_previous_jobs = max(machines, key=lambda machine: (machine[-1]['end_time'] if machine else 0))
        max_end_time_previous_jobs = max_end_time_previous_jobs[-1]['end_time'] if max_end_time_previous_jobs else 0
        # Calculate start and end times for the job
        start_time = max_end_time_previous_jobs # max(min_end_time_machine[-1]['end_time'] if min_end_time_machine else 0, 0)
        end_time = start_time + duration

        # Allocate the job to the machine
        machines[machines.index(min_end_time_machine)].append({'start_time': start_time, 'end_time': end_time, 'duration':duration, 'job_index': job_index})

    return machines

def pretty_print_allocated_jobs(machines):

    # Find the maximum end time among all machines
    max_end_time = max([machine[-1]['end_time'] for machine in machines if machine], default=0) + max([len(machine) for machine in machines])*2*len(machines)

    # Display the allocated jobs for each machine using bars
    for i, machine_jobs in enumerate(machines):
        print(f"Machine {i + 1}:", end=' ')

        for job in machine_jobs:
            duration:timedelta = job['duration']
            bar = '*' * int(duration.total_seconds()/60)
            print(f"[{bar:^{duration}}]", end='')

        # Fill the remaining time with spaces
        remaining_space = max_end_time - machine_jobs[-1]['end_time']
        print(f"[{' ':^{remaining_space}}]")


def allocate_jobs_to_machines_mod(graph: nx.DiGraph, num_machines = 8):
    machines = [[] for _ in range(num_machines)]
    queue = [n[0] for n in graph.in_degree if n[1] == 0]
    while len(queue) > 0:
        jobs_sorted = sorted(queue, key=lambda x: nx.get_node_attributes(graph, "duration")[x])
        
        max_end_time = max([machine[-1]['end_time'] for machine in machines if machine], default=0)
        for job in jobs_sorted:
            min_end_time_machine = min(machines, key=lambda machine: (machine[-1]['end_time'] if machine else 0))
            duration:timedelta = nx.get_node_attributes(graph, "duration")[job]
            start_time = max_end_time 
            end_time = start_time + duration.total_seconds()
            machines[machines.index(min_end_time_machine)].append({'start_time': start_time, 'end_time': end_time, 'duration':end_time-start_time, 'job_index': job})
        
        graph.remove_nodes_from(queue)
        graph.remove_edges_from([edge for edge in graph.edges if edge[0] in queue])
        queue = [n[0] for n in graph.in_degree if n[1] == 0]
    
    return machines
    
def convert_rustworkx_to_networkx(graph):
    """Convert a rustworkx PyGraph or PyDiGraph to a networkx graph."""
    edge_list = [
        [graph[x[0]], graph[x[1]] ]for x in graph.edge_list()]

    if isinstance(graph, rx.PyGraph):
        if graph.multigraph:
            return nx.MultiGraph(edge_list)
        else:
            return nx.Graph(edge_list)
    else:
        if graph.multigraph:
            return nx.MultiDiGraph(edge_list)
        else:
            return nx.DiGraph(edge_list) 
    
@profile
def allocate_jobs_to_machines_with_heuristic(graph: nx.DiGraph, num_machines=8):
    man_graph = graph.copy()
    jobs = {}
    queue = [n[0] for n in man_graph.in_degree if n[1] == 0]
    free_time = [0] * num_machines
    # Calculate critical path
    #critical_path = nx.dag_longest_path(man_graph, weight='duration')
    while len(queue) > 0:
        # Sort the jobs in the queue based on the critical path
        #jobs_sorted = sorted(queue, key=lambda x: critical_path.index(x) if x in critical_path else float('inf'))


        for job in queue:
            machine = min(range(num_machines), key=lambda machine: free_time[machine])
            duration = man_graph.nodes[job]["duration"]
            earliest_start_time_for_job = earliest_start_time(job, graph, jobs)
            # do machine choice after (by also taking into account how far back we can go)
            start_time = max([free_time[machine], earliest_start_time_for_job])
            end_time = start_time + duration.total_seconds()
            jobs[job] = {'start_time': start_time, 'end_time': end_time,
                                                                   'duration': end_time - start_time, 'machine_index': machine}
            free_time[machine] = end_time
            #print(free_time)
            #print("EST : ", earliest_start_time_for_job)
        successors = set(n for q in queue for n in man_graph.successors(q))
        man_graph.remove_nodes_from(queue)
        man_graph.remove_edges_from(man_graph.out_edges(queue))
        queue = [n for n in successors if man_graph.in_degree[n] == 0]

    return jobs


@profile
def allocate_jobs_to_machines_with_heuristic_rx(graph: (rx.PyDiGraph, dict), num_machines=8):
    man_graph = graph[0].copy()
    durations = graph[1]
    jobs = {}
    queue = [n for n in man_graph.node_indices() if man_graph.in_degree(n) == 0]

    free_time = [0] * num_machines

    
    while len(queue) > 0:
        for job in queue:
            job_index = man_graph.get_node_data(job)
            # print("Job : ", job)
            machine = min(range(num_machines), key=lambda machine: free_time[machine])
            duration = durations[job_index]
            earliest_start_time_for_job = earliest_start_time_optimized(job, graph[0],jobs) #todo
            # do machine choice after (by also taking into account how far back we can go)
            start_time = max([free_time[machine], earliest_start_time_for_job])
            end_time = start_time + duration.total_seconds()
            jobs[job_index] = {'start_time': start_time, 'end_time': end_time,
                                                                'duration': end_time - start_time, 'machine_index': machine}
            free_time[machine] = end_time

        # TODO: Do this but for this 
        successors = []
        out_edges = []
        for q in queue:
            for n in man_graph.successor_indices(q):
                out_edges.append((q,n))
                successors.append(n)
        successors = set(successors)
        
        man_graph.remove_edges_from(out_edges)
        man_graph.remove_nodes_from(queue)
        # print("QUEUE: ", queue)
        # def edge_filter(edge):
        #     print("EDGE: ", edge)
        #     return edge[0] in queue

        queue = [n for n in successors if man_graph.in_degree(n) == 0]

    
    
    return jobs
### TODO: Delete later


def heft(graph: nx.DiGraph, num_machines: int):
    tasks = list(graph.nodes)
    ranks = calculate_ranks(graph)

    # Initialize schedule and free times for each machine
    schedule = [[] for _ in range(num_machines)]
    free_time = [0] * num_machines

    # Sort tasks by decreasing order of rank
    sorted_tasks = sorted(tasks, key=lambda task: ranks[task], reverse=True)

    # Iterate through sorted tasks and allocate to machines
    for task in sorted_tasks:
        machine = select_machine(task, schedule, free_time)
        start_time = max([free_time[machine], earliest_start_time(task, graph, schedule)])
        end_time = start_time + nx.get_node_attributes(graph, "duration")[task].total_seconds()
        schedule[machine].append({'start_time': start_time, 'end_time': end_time, 'duration': end_time - start_time, 'job_index': task})
        free_time[machine] = end_time

    return schedule

@profile
def earliest_start_time(task, graph, schedule):
    # Calculate earliest start time for a task on a machine respecting dependencies
    dependencies = list(graph.predecessors(task))
    if not dependencies:
        return 0
    else:
        max_end_time = max(schedule[job_index]["end_time"] for job_index in dependencies )
        return max_end_time

@profile
def earliest_start_time_optimized(task, graph, schedule):
    # Calculate earliest start time for a task on a machine respecting dependencies
    dependencies = list(graph.predecessors(task))
    # print("task: ", task)
    # print("depend: ", dependencies)
    # print("schedule: ", schedule)
    if not dependencies:
        return 0
    else:
        max_end_time = max(schedule[job_index]["end_time"] for job_index in dependencies )
        return max_end_time
    
    
def calculate_ranks(graph: nx.DiGraph):
    ranks = {}
    for task in nx.topological_sort(graph):
        rank = calculate_rank(task, ranks, graph)
        ranks[task] = rank
    return ranks

def calculate_rank(task, ranks, graph, memo={}):
    if task in ranks:
        return ranks[task]
    elif task in memo:
        return memo[task]
    else:
        successors = list(graph.successors(task))
        if not successors:
            return nx.get_node_attributes(graph, "duration")[task]
        else:
            max_rank = max(calculate_rank(succ, ranks, graph, memo) for succ in successors)
            rank = nx.get_node_attributes(graph, "duration")[task] + max_rank
            memo[task] = rank  # Memoize the rank for this task
            return rank

def select_machine(task, schedule, free_time):
    # Dummy function for machine selection
    # You can implement a more sophisticated strategy based on machine capabilities
    return min(range(len(schedule)), key=lambda machine: free_time[machine])

if __name__ == "__main__":
    import data_loader
    #dag = data_loader.load_dag_from_json("./data/xlargeComplex.json")
    # critical_path = nx.dag_longest_path(dag, weight='duration')
    # node_attrs = nx.get_node_attributes(dag, "duration")
    # critical_path_length = sum([node_attrs[node].total_seconds() for node in critical_path])
    # schedule = allocate_jobs_to_machines_with_heuristic(dag, num_machines=64)
    
    dag = data_loader.load_dag_from_json_rx("./data/MediumComplex.json")
    
    critical_path = rx.dag_weighted_longest_path(dag[0], weight_fn=lambda src, _, __: dag[1][dag[0].get_node_data(src)].total_seconds())
    critical_path_length = sum([dag[1][dag[0].get_node_data(node)].total_seconds() for node in critical_path])
    schedule = allocate_jobs_to_machines_with_heuristic_rx(dag, num_machines=10)
    del dag
    
    machines = [[] for _ in range(10)]
    
    for job_index,job_data in schedule.items():
        job_data["job_index"] = job_index
        machines[job_data["machine_index"]].append(job_data)
    for i in range(len(machines)):
        machines[i] = sorted(machines[i], key=lambda e: e["start_time"])
    del schedule
    pers_makespan = []
    for machine in machines:
        pers_makespan.append(machine[-1]['end_time'])
    makespan = max(pers_makespan)
    
    print("MAKE_SPAN: ", makespan)
    print("SLR: ", makespan/critical_path_length)
    print("CRITICAL PATH: ", critical_path_length)
    # import timeit
    # start_time = timeit.default_timer()
    # nx.topological_sort(dag)
    # elapsed = timeit.default_timer() - start_time
    # print("NX TOPOSORT:", elapsed)  # TODO: timeit for JSON file loading
    # del dag
    # dag_rx = data_loader.load_dag_from_json_rx("./data/xlargeComplex.json")

    # start_time = timeit.default_timer()
    # rx.topological_sort(dag_rx[0])
    # elapsed = timeit.default_timer() - start_time
    # print("RX TOPOSORT:", elapsed)  # TODO: timeit for JSON file loading