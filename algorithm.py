import networkx as nx
import rustworkx as rx
from datetime import datetime, timedelta

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
    
#@profile    
def allocate_jobs_to_machines_with_heuristic(graph: nx.DiGraph, num_machines=8):
    man_graph = graph.copy()
    machines = [[] for _ in range(num_machines)]
    queue = [n[0] for n in man_graph.in_degree if n[1] == 0]
    print("queue : ", queue)
    free_time = [0] * num_machines
    # Calculate critical path
    critical_path = nx.dag_longest_path(man_graph, weight='duration')

    while len(queue) > 0:
        # Sort the jobs in the queue based on the critical path
        jobs_sorted = sorted(queue, key=lambda x: critical_path.index(x) if x in critical_path else float('inf'))
        print("jobs_sorted : ", jobs_sorted)


        for job in jobs_sorted:
            machine = min(range(len(machines)), key=lambda machine: free_time[machine])
            duration = nx.get_node_attributes(man_graph, "duration")[job]
            earliest_start_time_for_job = earliest_start_time(job, graph, machines)
            # do machine choice after (by also taking into account how far back we can go)
            start_time = max([free_time[machine], earliest_start_time_for_job])
            end_time = start_time + duration.total_seconds()
            machines[machine].append({'start_time': start_time, 'end_time': end_time,
                                                                   'duration': end_time - start_time, 'job_index': job})
            free_time[machine] = end_time
            #print(free_time)
            #print("EST : ", earliest_start_time_for_job)

        man_graph.remove_nodes_from(queue)
        man_graph.remove_edges_from([edge for edge in man_graph.edges if edge[0] in queue])
        queue = [n[0] for n in man_graph.in_degree if n[1] == 0]

    return machines

# TODO: Consider handling isolates separately 

@profile
def allocate_jobs_to_machines_with_heuristic_optimized(graph: nx.DiGraph,durations, num_machines=8):
    man_graph = rx.networkx_converter(graph)
    machines = [[] for _ in range(num_machines)]
    queue = filter(lambda n: man_graph.in_degree(n) == 0, man_graph.node_indices())
    print("queue : ", queue)
    free_time = [0] * num_machines
    # Calculate critical path
    critical_path = rx.dag_weighted_longest_path(man_graph, weight_fn=lambda src, _, __: durations[man_graph.get_node_data(src)].total_seconds()) # I still need attributes for this piece

    while True:
        try:
            element = next(queue)
            # Sort the jobs in the queue based on the critical path
            jobs_sorted = sorted(queue, key=lambda x: list(critical_path).index(x) if x in critical_path else float('inf'))
            print("jobs_sorted : ", [man_graph.get_node_data(x) for x in jobs_sorted])

            for job in jobs_sorted:
                job_index = man_graph.get_node_data(job)
                machine = min(range(len(machines)), key=lambda machine: free_time[machine])
                duration = durations[job]
                earliest_start_time_for_job = earliest_start_time_optimized(job, graph,machines)
                # do machine choice after (by also taking into account how far back we can go)
                start_time = max([free_time[machine], earliest_start_time_for_job])
                end_time = start_time + duration.total_seconds()
                machines[machine].append({'start_time': start_time, 'end_time': end_time,
                                                                    'duration': end_time - start_time, 'job_index': job_index})
                free_time[machine] = end_time
                #print(free_time)
                #print("EST : ", earliest_start_time_for_job)

            man_graph.remove_nodes_from(queue)
            man_graph.remove_edges_from(man_graph.filter_edges(lambda edge: edge[0] in queue))
            queue = filter(lambda n: man_graph.in_degree(n) == 0, man_graph.node_indices())
        except StopIteration:
            break



    return machines

def earliest_start_time_optimized(task, graph, schedule):
    # Calculate earliest start time for a task on a machine respecting dependencies
    print("task : ", task)
    print("schedule :", schedule) 
    dependencies = list(graph.predecessors(task))
    print(dependencies)
    if not dependencies:
        return 0
    else:
        max_end_time = max([job['end_time'] for machine_schedule in schedule for job in machine_schedule if job['job_index'] in dependencies])
        return max_end_time

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

def earliest_start_time(task, graph, schedule):
    # Calculate earliest start time for a task on a machine respecting dependencies
    dependencies = list(graph.predecessors(task))
    if not dependencies:
        return 0
    else:
        max_end_time = max([job['end_time'] for machine_schedule in schedule for job in machine_schedule if job['job_index'] in dependencies])
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



# This is only here for use with kernprof line_profiler
if __name__ == "__main__":
    import data_loader
    dag, durations = data_loader.load_dag_from_json("./data/xsmallComplex.json", rustwork=True)
    # man_graph = rx.networkx_converter(dag)
    # print(man_graph.get_node_data(1180))
    # print(set(man_graph.nodes()).symmetric_difference(set(durations.keys())))
    
    schedule = allocate_jobs_to_machines_with_heuristic_optimized(dag, durations, num_machines=3)
    #schedule = allocate_jobs_to_machines_with_heuristic(dag, num_machines=3)
    
    