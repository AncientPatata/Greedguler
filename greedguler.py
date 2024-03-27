import argparse
import algorithm
import data_loader
import json 
from cProfile import Profile
from pstats import SortKey, Stats

if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog='greedguler')
    parser.add_argument('num_machines', type=int, help='Number of machines')
    parser.add_argument('--file', help='Path to the file containing the DAG (optional)')
    parser.add_argument('--gen', action='store_true', help='Generate a random DAG (optional)')
    parser.add_argument('--num_nodes', type=int, help='Number of nodes in the DAG (required if --gen is used)')
    parser.add_argument('--max_duration', type=int, help='Maximum duration of jobs in the DAG (required if --gen is used)')
    parser.add_argument("--profile", action="store_true", help="Whether or not to profile the algorithm code")
    args = parser.parse_args()

    if args.gen:
        if not (args.num_nodes and args.max_duration):
            parser.error("--gen requires --num_nodes and --max_duration.")
        dag = data_loader.generate_random_dag(args.num_nodes, args.max_duration)
    elif args.file:
        dag = data_loader.load_dag_from_json(args.file)
    else:
        parser.error("Either --file or --gen must be provided.")
    if args.profile:
        with Profile() as profile:
            schedule = algorithm.allocate_jobs_to_machines_with_heuristic(dag, num_machines=args.num_machines)
            (
            Stats(profile)
            .strip_dirs()
            .sort_stats(SortKey.CALLS)
            .print_stats()
            )
    else:
        schedule = algorithm.allocate_jobs_to_machines_with_heuristic(dag, num_machines=args.num_machines)
    
    
    with open("schedule.json", "w") as file_handle:
        json.dump(schedule, file_handle)
    #print(schedule)