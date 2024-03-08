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
            duration = job['duration']
            bar = '*' * duration
            print(f"[{bar:^{duration}}]", end='')

        # Fill the remaining time with spaces
        remaining_space = max_end_time - machine_jobs[-1]['end_time']
        print(f"[{' ':^{remaining_space}}]")

# Example usage
job_durations = [4, 2, 5, 3, 7, 9,1]
result = allocate_jobs_to_machines(job_durations, 4)

# Display the allocated jobs for each machine
for i, machine_jobs in enumerate(result):
    print(f"Machine {i + 1}: {machine_jobs}")

pretty_print_allocated_jobs(result)