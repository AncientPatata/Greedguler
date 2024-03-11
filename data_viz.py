import plotly.express as px
import plotly.figure_factory as ff
import json 
import pandas as pd
from datetime import datetime

if __name__ == "__main__":
    with open("schedule.json") as file_handle:
        schedule = json.load(file_handle)
        job_list = [] #[{"start_time": 0, "end_time": 5.3, "machine": 1},{"start_time": 1.05, "end_time": 3, "machine": 2}]
        for (index, machine_jobs) in enumerate(schedule):
            machine = "Machine " + str(index+1)
            job_list += [{"job_index": job["job_index"],"start_time": datetime.fromtimestamp(job["start_time"]), "end_time": datetime.fromtimestamp(job["end_time"]), "duration": job["duration"], "machine": machine} for job in machine_jobs] #[dict(job, **{"machine": machine}) for job in machine_jobs[:10] ]
            
        df = pd.DataFrame(job_list)
        print(df.head())
        fig = px.timeline(df, x_start="start_time", x_end="end_time", y="machine", color="machine", hover_data="job_index")
        #fig.update_layout(xaxis_type='linear')
        fig.write_html('schedule_viz.html', auto_open=True)
        
