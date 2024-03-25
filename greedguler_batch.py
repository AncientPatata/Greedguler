import argparse
import os
import subprocess
import time
from azure.batch import BatchServiceClient
from azure.batch import models
from azure.batch.batch_auth import SharedKeyCredentials
from azure.storage.blob import BlobServiceClient, BlobClient
import json
import configs


def create_pool(batch_client, name_pool, cmd_s_task=None, rule_scale_pool=None):

    #parameter image node
    param_image = models.VirtualMachineConfiguration(
        image_reference = models.ImageReference(
        offer = '0001-com-ubuntu-server-focal',
        publisher = 'canonical',
        sku = '20_04-lts',
        version = 'latest',
        virtual_machine_image_id = None
        ) ,
      node_agent_sku_id = 'batch.node.ubuntu 20.04'
    )

    #parameter pool
    new_pool = models.PoolAddParameter(
        id = name_pool, 
        vm_size = 'standard_d1_v2',
        virtual_machine_configuration = param_image,
        enable_inter_node_communication = True,
        enable_auto_scale = True,
        auto_scale_formula = rule_scale_pool,
        auto_scale_evaluation_interval = 'PT5M'
        )
    batch_client.pool.add(new_pool)



def create_job(batch_client, name_job, name_pool, cmd_prep_task=None):

    user = models.UserIdentity(
    auto_user = models.AutoUserSpecification(
        elevation_level = models.ElevationLevel.admin,
        scope = models.AutoUserScope.task
        )
    )

    prepare_task = models.JobPreparationTask(
        command_line = cmd_prep_task,
        id = None,
        user_identity = user
        )

    job = models.JobAddParameter(
        id = name_job,
        pool_info = models.PoolInformation(pool_id = name_pool),
        job_preparation_task = prepare_task
        )
    batch_client.job.add(job)
    
    

def create_task(batch_client, name_job, cmd, name_task, param_multi_inst=None):

    current_date = time.localtime()[0:5]
    current_date = "{0}{1}{2}{3}{4}".format(
                                            current_date[0],current_date[1],
                                            current_date[2],current_date[3],
                                            current_date[4]
                                           )

    dest_files_in_container = models.OutputFileBlobContainerDestination(
        container_url = f"{configs.blob_container['url']}{configs.blob_container['sas_token']}",
        path = f"{name_job}/{name_task}/{current_date}"
        )

    dest_files = models.OutputFileDestination(container = dest_files_in_container )
    with open(f'intermediates/outpath_{name_task}_{current_date}.json', "w") as f:
        json.dump(dest_files.serialize(), f, indent=4)

    trigger_upload = models.OutputFileUploadOptions(upload_condition = 'taskCompletion')

    upload_files = models.OutputFile(
                                     file_pattern = '$AZ_BATCH_TASK_DIR/*' ,
                                     destination = dest_files,
                                     upload_options = trigger_upload
                                    )
    outputs = []
    outputs.append(upload_files)
    tache = models.TaskAddParameter(
        id = name_task, command_line = cmd,
        multi_instance_settings = param_multi_inst,
        resource_files = None, environment_settings = None,
        output_files = outputs
        )
    batch_client.task.add(name_job,tache)
    return dest_files


def download_files_from_blob(blob_service_client:BlobServiceClient):
    container_client = blob_service_client.get_container_client("results")
    
    blobs = container_client.list_blobs()
    for blob in blobs:
        blob_client = container_client.get_blob_client(blob=blob.name)  # Use blob.name
        download_file_path = os.path.join("./results", blob.name)
        os.makedirs(os.path.dirname(download_file_path), exist_ok=True)
        with open(download_file_path, "wb") as download_file:
            download_file.write(blob_client.download_blob().readall())
            
        print(f"Downloaded {blob.name} to {download_file_path}")


def git_push_changes(repo_dir, commit_message="Automated Repo Update"):
    """
    Pushes changes in the specified directory to the remote Git repository and waits until the operation is complete.
    This function ensures that the current working directory is reverted back to its original path after operation.
    :param repo_dir: Directory of the Git repository.
    :param commit_message: Commit message.
    """
    original_dir = os.getcwd()  # Store the original working directory
    try:
        os.chdir(repo_dir)
        
        # Check if there are changes to commit
        status_result = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True)
        if status_result.stdout.strip() == "":
            print("No changes to commit.")
            return
        
        # Add all changes to git
        subprocess.run(["git", "add", "."], check=True)
        
        # Commit the changes
        try:
            subprocess.run(["git", "commit", "-m", commit_message], check=True)
        except subprocess.CalledProcessError as e:
            # This might happen if there's nothing to commit, so it's safe to ignore
            print(f"Nothing to commit. ({e})")
        
        # Push the changes
        subprocess.run(["git", "push"], check=True)
        
        print("Changes pushed to the repository.")
    finally:
        os.chdir(original_dir)  # Revert back to the original working directory ..



if __name__ == "__main__":
    
    
    parser = argparse.ArgumentParser(
                                    description='Sending a task to a job.',
                                    formatter_class=argparse.ArgumentDefaultsHelpFormatter
                                    )
    parser.add_argument('--job_id', help='Id of job', dest='job_id', default="GreedgulerJob3")
    parser.add_argument('--task_id', help='Id of task', dest='task_id', default='GreedgulerTask0')
    parser.add_argument('--pool_id', help='Id of pool', dest='task_id', default='GreedgulerPool3')
    parser.add_argument('--new_job', help='Id of new job to create', dest='new_job')
    parser.add_argument('--new_pool', help='Id of new pool to create', dest='new_pool')
    
    args = parser.parse_args()
    
    credentials_batch = SharedKeyCredentials(account_name = configs.batch['name'], key = configs.batch['key'])
    batch_client = BatchServiceClient(credentials = credentials_batch, batch_url = configs.batch['url'])
    blob_service_client = BlobServiceClient(account_url=configs.blob_container["url"], credential=configs.blob_container["sas_token"])    
    
    pool_id = "GreedgulerPool0"

    if args.new_pool:
    
        create_pool(
            batch_client = batch_client,
            name_pool = args.new_pool,
            rule_scale_pool = configs.rule_scaling
            )

        pool_id = args.new_pool

        print("Pool Created: {0}\n".format(pool_id))
        with open('output_pool_id_job_id.txt','a') as file_resource:
            file_resource.write("\nPool created: {0}\n".format(pool_id))
    else:
        pool_id = args.pool_id

    if args.new_job:
        
        create_job(
                batch_client = batch_client,
                name_job = args.new_job,
                name_pool = pool_id, 
                cmd_prep_task = configs.cmd_prep_task
                )


        job_id = args.new_job
        print("Job created: {0}\n".format(job_id))
        with open('output_pool_id_job_id.txt','a') as file_resource:
            file_resource.write("\nJob created: {0}\n".format(job_id))

    else:
        job_id = args.job_id
    


        

    
    task_id = args.task_id
    
    multi_instance_task_param = models.MultiInstanceSettings(
                         coordination_command_line = configs.coordination_command ,
                         number_of_instances = min(configs.nb_processes,5),
                         common_resource_files = None
                        )
    

    # Push changes to the azure_batch repo before creating the task
    git_push_changes("./azure_batch")

    dest_files = create_task(
                batch_client = batch_client,
                name_job = job_id,
                cmd = configs.start_command,
                name_task = task_id,
                param_multi_inst = multi_instance_task_param
               )
    
    # Monitoring the task status
    while True:
        task = batch_client.task.get(job_id, task_id)
        print(f"Task {task_id} status: {task.state}")
        if task.state == 'completed':
            print("Task completed. Downloading files from blob ... ")
            download_files_from_blob(blob_service_client)
            print("Download finished.")
        time.sleep(10)  # Polling interval


