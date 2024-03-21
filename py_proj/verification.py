from algorithm import *
from data_loader import *

# job_durations = [4, 2, 5, 3, 7, 9, 1]
# schedule = allocate_jobs_to_machines(job_durations, 4)


def read_json(filepath):
    with open(filepath, "r") as file_handle:
        data = json.load(file_handle)
    return data


def verifcation_overlap_machine(schedule):
    # Create a dictionary to track the job timeline for each machine
    # Check if there is any overlap in job start and end times for each machine
    
    for machine_schedule in schedule:
        # Sort if not already sorted
        for i in range(len(machine_schedule) - 1):
            if machine_schedule[i]["end_time"] > machine_schedule[i + 1]["start_time"]:
                return False
        else:
            return True


def verification_dependencies(graph, schedule):
    for machine_schedule in schedule:
        for job_details in machine_schedule:
            job_index = job_details['job_index']
            dependencies = list(graph.predecessors(job_index))
            # print(job_index, "is after:", dependencies)
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

