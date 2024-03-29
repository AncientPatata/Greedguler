import networkx as nx
import rustworkx as rx
from datetime import datetime, timedelta



#DEPRECTAED
def pretty_print_allocated_jobs(machines):
    """
    Prints a visual representation of job allocations across multiple machines.
    Each machine's allocated jobs are displayed as bars, where the length of the bar
    represents the job's duration. The output is designed to give a quick visual overview
    of the workload distribution among the machines.

    Args:
    - machines (list of lists of dicts): A nested list where each sublist represents a machine
    and contains dictionaries with job details, including 'end_time' and 'duration' keys.
    Returns:
    - None: This function prints the job allocations to stdout and does not return any value.
    """
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


    
def allocate_jobs_to_machines_nx(graph: nx.DiGraph, num_machines=8):
    """
    Allocates jobs to machines based on a directed graph of job dependencies using NetworkX.

    This function attempts to optimize job allocation by considering the critical path and
    job dependencies to minimize overall completion time across a specified number of machines.

    Args:
    - graph (nx.DiGraph): A directed graph where nodes represent jobs, and edges represent dependencies.
    - num_machines (int, optional): The number of machines available for job allocation. Defaults to 8.
    Returns:
    - machines (list of lists of dicts): A nested list where each sublist represents the allocation of jobs to a machine. Each job is represented as a dictionary containing 'start_time', 'end_time',
      'duration', and 'job_index'.
    """
    man_graph = graph.copy()
    machines = [[] for _ in range(num_machines)]
    queue = [n[0] for n in man_graph.in_degree if n[1] == 0]
    free_time = [0] * num_machines
    # Calculate critical path
    critical_path = nx.dag_longest_path(man_graph, weight='duration')

    while len(queue) > 0:
        # Sort the jobs in the queue based on the critical path
        jobs_sorted = sorted(queue, key=lambda x: critical_path.index(x) if x in critical_path else float('inf'))


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


#@profile
def leveled_topological_sort(graph: rx.PyDiGraph):
    """
    Performs a leveled topological sort on a directed graph.

    This function iterates through the graph, removing nodes with no incoming edges (indicating
    no dependencies) and their associated edges, effectively sorting the nodes in a way that respects
    their dependencies. The sorting is "leveled" in the sense that it groups nodes by their distance
    from the start nodes (with no dependencies).

    Args:
    - graph (rx.PyDiGraph): A directed graph where nodes represent tasks and edges represent dependencies.
    Returns:
    - None: This function modifies the graph in-place and does not return a value.
    """
    node_queue = [[n for n in graph.node_indices() if graph.in_degree(n) == 0]]
    not_done= True 
    while not_done:
        successors = []
        out_edges = []
        for q in node_queue:
            for n in graph.successor_indices(q):
                out_edges.append((q,n))
                successors.append(n)
        successors = set(successors)
        
        graph.remove_edges_from(out_edges)
        graph.remove_nodes_from(node_queue)

        node_queue = [n for n in successors if graph.in_degree(n) == 0]

def earliest_start_time_optimized(task, graph, schedule):
    """
    Calculates the earliest start time for a given task based on its dependencies.

    This function examines a task's dependencies within a directed graph and determines the
    earliest time the task can start, based on the completion times of its dependencies.

    Args:
    - task (int/str): The identifier for the task whose earliest start time is being calculated.
    - graph (Directed Graph): The graph representing task dependencies.
    - schedule (dict): A dictionary where keys are task identifiers and values are dictionaries
    containing 'end_time' among other scheduling details.
    Returns:
    - int: The earliest start time for the given task.
    """
    dependencies = list(graph.predecessors(task))

    if not dependencies:
        return 0
    else:
        max_end_time = max(schedule.get(job_index, {"end_time": 0})["end_time"] for job_index in dependencies )
        return max_end_time

# @profile
def allocate_jobs_to_machines_with_heuristic_rx(graph: (rx.PyDiGraph, dict), num_machines=8):
    """
    Allocates jobs to machines using a heuristic approach on a directed graph with retworkx.

    This function takes a graph representing job dependencies and a dictionary of job durations,
    then allocates jobs to machines aiming to minimize overall completion time. It uses an
    optimized approach for determining the earliest start time for each job based on its dependencies.

    Args:
    - graph (tuple): A tuple containing a retworkx PyDiGraph and a dictionary of job durations.
    - num_machines (int, optional): The number of machines available for allocation. Defaults to 8.
    Returns:
    - jobs (dict): A dictionary where each key is a job index and each value is a dictionary containing 'start_time', 'end_time', 'duration', and 'machine_index' for the job.
    """
    man_graph = graph[0].copy()
    durations = graph[1]
    jobs = {}
    queue = [n for n in man_graph.node_indices() if man_graph.in_degree(n) == 0]

    free_time = [0] * num_machines

    
    while len(queue) > 0:
        for job in queue:
            job_index = man_graph.get_node_data(job)
            machine = min(range(num_machines), key=lambda machine: free_time[machine])
            duration = durations[job_index]
            earliest_start_time_for_job = earliest_start_time_optimized(job, graph[0],jobs) #todo
            start_time = max([free_time[machine], earliest_start_time_for_job])
            end_time = start_time + duration.total_seconds()
            jobs[job_index] = {'start_time': start_time, 'end_time': end_time,
                                                                'duration': end_time - start_time, 'machine_index': machine}
            free_time[machine] = end_time

        successors = []
        out_edges = []
        for q in queue:
            for n in man_graph.successor_indices(q):
                out_edges.append((q,n))
                successors.append(n)
        successors = set(successors)
        
        man_graph.remove_edges_from(out_edges)
        man_graph.remove_nodes_from(queue)


        queue = [n for n in successors if man_graph.in_degree(n) == 0]


def transform_allocation_format(jobs, num_machines):
    """
    Transforms the job allocation format from a dictionary with job indexes as keys to a list of
    lists of dictionaries, where each sublist represents the jobs allocated to a machine, sorted
    by their start times.

    Args:
    - jobs (dict): A dictionary where each key is a job index and each value is a dictionary
    containing 'start_time', 'end_time', 'duration', and 'machine_index' for the job.
    - num_machines (int): The number of machines jobs are allocated to.
    Returns:
    - machines (list of lists of dicts): A nested list where each sublist represents the allocation of jobs to a machine, sorted by their start time. Each job is represented as a dictionary containing
      'start_time', 'end_time', 'duration', and 'job_index'.
    """
    # Initialize a list for each machine
    machines = [[] for _ in range(num_machines)]

    # Populate the machines list with jobs
    for job_index, job_details in jobs.items():
        machine_index = job_details['machine_index']
        # Add the job to the corresponding machine, including the job index in the dictionary
        machines[machine_index].append({
            'start_time': job_details['start_time'],
            'end_time': job_details['end_time'],
            'duration': job_details['duration'],
            'job_index': job_index
        })

    # Sort the jobs by start time within each machine
    for machine_jobs in machines:
        machine_jobs.sort(key=lambda job: job['start_time'])

    return machines

### HEFT Algorithm code 

def heft(graph: nx.DiGraph, num_machines: int):
    """Implements the core HEFT algorithm. It schedules tasks (nodes in the DAG) across a given number of machines to minimize the overall execution time.

    Args:
        graph (nx.DiGraph): A networkx directed acyclic graph where nodes represent tasks and edges represent dependencies between tasks. Each node has a 'duration' attribute indicating the task's execution time.
        num_machines (int): The number of machines available for executing these tasks.

    Returns:
    Any: A schedule that is a list of lists. Each sublist represents the schedule for a machine, containing dictionaries with keys 'start_time', 'end_time', 'duration', and 'job_index', detailing each task's scheduling.
    """
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
    """Calculates the earliest start time for a task on any machine, considering the task dependencies and the current schedule.

    Args:
        task (dict): The task for which to calculate the earliest start time.
        graph (nx.DiGraph): The DAG of tasks.
        schedule (Any): The current schedule of tasks on machines.

    Returns:
    float: The earliest time at which the specified task can start executing.
    """
    dependencies = list(graph.predecessors(task))
    if not dependencies:
        return 0
    else:
        max_end_time = max([job['end_time'] for machine_schedule in schedule for job in machine_schedule if job['job_index'] in dependencies])
        return max_end_time

def calculate_ranks(graph: nx.DiGraph):
    """Calculates the priority rank for each task in the graph, which is used to order tasks for scheduling. The rank of a task is the longest path from it to an exit task, including its own duration.

    Args:
        graph (nx.DiGraph): The DAG of tasks.

    Returns:
    dict: A dictionary mapping each task to its rank.
    """
    ranks = {}
    for task in nx.topological_sort(graph):
        rank = calculate_rank(task, ranks, graph)
        ranks[task] = rank
    return ranks

def calculate_rank(task, ranks, graph, memo={}):
    """ Recursively calculates the rank of a given task. Utilizes memoization to avoid recalculating ranks for tasks.

    Args:
        task (Any): The task for which to calculate the rank.
        ranks (dict):  A dictionary of precomputed ranks for some tasks.
        graph (nx.DiGraph): The DAG of tasks.
        memo (dict, optional): A dictionary used for memoization of task ranks. Defaults to {}.

    Returns:
    Any: The rank of the specified task.
    """
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