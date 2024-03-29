from algorithm import *
from data_loader import *


def read_json(filepath):
    '''
    Function to read JSON data from a file

    Args:
        filepath (str): Path to the JSON file

    Returns:
        dict: JSON data read from the file
    '''
    with open(filepath, "r") as file_handle:
        data = json.load(file_handle)
    return data


def verifcation_overlap_machine(schedule):
    '''
    Verify if there is any overlap in job scheduling for each machine

    Args:
        schedule (list): List of schedules for each machine

    Returns:
        bool: True if no overlap is found, False otherwise
    '''
    for machine_schedule in schedule:
        for i in range(len(machine_schedule) - 1):
            if machine_schedule[i]["end_time"] > machine_schedule[i + 1]["start_time"]:
                return False
    return True


def verification_dependencies(graph, schedule):
    '''
    Verify if all job dependencies are satisfied in the schedule

    Args:
        graph (networkx.DiGraph): Directed acyclic graph representing job dependencies
        schedule (list): List of schedules for each machine

    Returns:
        bool: True if all dependencies are satisfied, False otherwise
    '''
    for machine_schedule in schedule:
        for job_details in machine_schedule:
            job_index = job_details['job_index']
            dependencies = list(graph.predecessors(job_index))
            for dependency in dependencies:
                for previous_machine_schedule in schedule:
                    for previous_job_details in previous_machine_schedule:
                        if previous_job_details['job_index'] == dependency:
                            dependency_end_time = previous_job_details['end_time']
                            job_start_time = job_details['start_time']
                            if dependency_end_time > job_start_time:
                                print(
                                    f"Error: Dependency of job {job_index} not satisfied.")
                                return False
    print("All dependencies are satisfied.")
    return True


if __name__ == "__main__":
    filepath = 'data/smallRandom.json'
    schedule_data = read_json(filepath)
    graph = load_dag_from_json(filepath)
    schedule = allocate_jobs_to_machines_mod(graph, num_machines=8)

    verifcation_overlap_machine(schedule)
    verification_dependencies(schedule_data, schedule)


    verifcation_overlap_machine(schedule)
    verification_dependencies(schedule_data, schedule)

