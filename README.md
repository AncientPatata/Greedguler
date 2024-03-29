# Greedguler

Greedguler is a Python-based scheduler designed to optimize task assignments using the greedy algorithm. It is aimed at managing and distributing tasks across multiple nodes, focusing on achieving minimal overall duration by considering various constraints and dependencies.

## Features

- **Task Scheduling:** Dynamically schedules tasks based on their dependencies and execution times.
- **Greedy Algorithm Implementation:** Utilizes a greedy algorithm for efficient task distribution.
- **Data Visualization:** Includes tools for visualizing task schedules and system performance.
- **Extensible:** Easy to modify and extend for various scheduling criteria and algorithms.

## Getting Started

### Prerequisites

Ensure you have Python 3.6 or later installed on your system. Dependencies are listed in `requirements.txt`. You can also generate a virtual environment in VS Code.

### Installation

Clone the repository to your local machine:

```bash
git clone https://github.com/AncientPatata/Greedguler.git
```

Install the required Python packages:

```bash
cd Greedguler
pip install -r requirements.txt
```

If you want to use logging, you need to add your `NGROK_AUTHTOKEN` to your config file.
Moreover, you need to replace the backblaze API id and API key in the [https://github.com/AncientPatata/azure_batch_greedguler/](Asure batch repo) with your own (I only put in some mock ones).

## Usage

There is [https://greedguler.readthedocs.io/en/latest/index.html](full documentation) for the codebase. We will now go over the different files that you can run and the commandline arguments.

### `greedguler.py`

This script schedules tasks across different machines using a greedy algorithm approach.

- **`num_machines`**: The number of machines available for scheduling tasks. This argument is mandatory.
- **`--file`**: (Optional) Specifies the path to the JSON file containing the Directed Acyclic Graph (DAG) of tasks and dependencies. If not provided, the `--gen` flag must be used.
- **`--gen`**: (Optional) Triggers the generation of a random DAG. This flag requires `--num_nodes` and `--max_duration` to be specified.
- **`--num_nodes`**: Specifies the number of nodes (tasks) in the DAG when generating a random DAG with `--gen`.
- **`--max_duration`**: Sets the maximum duration of tasks in the DAG when generating a random DAG with `--gen`.
- **`--profile`**: (Optional) Enables profiling of the algorithm's execution for performance analysis.

Example usage:

```shell
python greedguler.py 5 --file path/to/dag.json
python greedguler.py 5 --gen --num_nodes 100 --max_duration 10
```

### `greedguler_batch.py`

This script facilitates the execution of tasks in batch mode, utilizing cloud computing resources for scheduling.

- **`--job_id`**: Specifies the job ID. This is used when sending tasks to the cloud.
- **`--task_id`**: Indicates the task ID for the job being executed.
- **`--pool_id`**: Defines the pool ID where the job will be executed.
- **`--new_job`**: (Optional) Specifies the ID for a new job to create. If omitted, an existing job ID must be provided.
- **`--new_pool`**: (Optional) Indicates the ID for a new pool to create for executing the job. If not provided, an existing pool ID must be used.

Example usage:

```shell
python greedguler_batch.py --job_id GreedgulerJob --task_id Task1 --pool_id GreedgulerPool
```

### `data_viz.py`

This script visualizes the scheduling of tasks on different machines.

- **`--num_machines`**: Specifies the number of machines for the visualization. Default is 3.
- **`--schedule_only`**: (Optional) A list of paths to the JSON files containing schedules to visualize. Multiple files can be specified, separated by spaces.
- **`--file`**: (Optional) Path to the DAG file for generating schedules to visualize.
- **`--gen`**: (Optional) Generates a random DAG for visualization. Requires `--num_nodes` and `--max_duration`.
- **`--num_nodes`**: Number of nodes in the DAG when generating a random DAG.
- **`--max_duration`**: Maximum duration of tasks in the DAG when generating a random DAG.
- **`--density`**: (Optional) Sets the edge density level for the generated DAG. Default is 1.
- **`--reload`**: (Optional) Reloads a previously generated DAG from a file for rescheduling and visualization.
- **`--nograph`**: (Optional) Use this flag to skip rendering a large graph for performance reasons.

Example usage:

```shell
python data_viz.py --num_machines 3 --file path/to/dag.json
python data_viz.py --num_machines 5 --gen --num_nodes 100 --max_duration 10
```
