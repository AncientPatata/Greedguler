#import argpars
import algorithm
import data_loader
import json 

if __name__ == "__main__":
    # parser = argparse.ArgumentParser(
    #                 prog='greedguler')
    
    # parser.add_argument('data')
    # parser.add_argument('num_machines')
    
    #dag = data_loader.load_dag_from_json("./smallComplex.json")
    dag = data_loader.generate_random_dag(12,86)
    schedule = algorithm.allocate_jobs_to_machines_mod(dag ,num_machines=3)
    #print(schedule)
    with open("schedule.json", "w") as file_handle:
        json.dump(schedule, file_handle)
    #algorithm.pretty_print_allocated_jobs(schedule)