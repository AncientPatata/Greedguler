#import argpars
import algorithm
import data_loader

if __name__ == "__main__":
    # parser = argparse.ArgumentParser(
    #                 prog='greedguler')
    
    # parser.add_argument('data')
    # parser.add_argument('num_machines')
    
    dag = data_loader.load_dag_from_json("./smallComplex.json")
    schedule = algorithm.allocate_jobs_to_machines_mod(dag)
    print(schedule)
    #algorithm.pretty_print_allocated_jobs(schedule)