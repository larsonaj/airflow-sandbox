

# airflow-sandbox

## Cloning the repository 

Before getting started, create a new folder on your desktop. If you already have a place where you like to store git repos or personal projects, feel free to clone the repo there. 

After installing git, open a terminal session and execute the following command:

```zsh
git clone https://github.com/larsonaj/airflow-sandbox.git
```

Now you should be able to open the repository in your IDE.


## Getting the Airflow containers started on your machine
*Note: this section assumes you have docker installed*
*ADD NOTE FOR MACOS USERS?*

After cloning the repo and installing docker, before starting the Airflow containers you need to prepare your environment variables.

First we need to add the *.env* file to the top level directory which contains authentication information for connections with Snowflake. 

Sample *.env* file:

```json
AIRFLOW_UID=50000  
SNOWFLAKE_CONNECTION='{
    "conn_type": "snowflake",
    "login": "username",
    "password": "password",
    "host": "captech_partner.snowflakecomputing.com",
    "port": 443,
    "schema": "F1",
    "extra": {
        "account": "captech_partner",
        "database": "TEST_DB",
        "region": "us-east-1",
        "warehouse": "XS_WH"
	}
}'
```

Once you have Docker installed and the env file created, in your terminal enter the following command:

```zsh
# To start docker on your first run? (can't remember if i had to do this to start)
docker compose up airflow-init

# To start docker after intial run?
docker compose up
```

This command starts the containers defined in this repo. It is able to pick up the container from its previous state and recreate it by using the docker-compose.yml file. Now that the cluster has started, you should now be able to access the Airflow UI at http://localhost:8080.

Reference: https://airflow.apache.org/docs/apache-airflow/stable/howto/docker-compose/index.html


## Understanding the initial DAG

At this point in the documentation, the Airflow containers should be spun up and you should have access to the Airflow UI. Next we can write our first DAG. 

DAGs (Directed Acyclic Graph) are a core concept in Airflow, they collect Tasks, organized with dependencies and relationships to say how they should run. In the sandbox, we have an example DAG that runs a predefined query against a Snowflake database before processing the data and storing the results in a new schema. 

Each Task in this DAG is defined by an Operator. Each operator is a step in this process, they contain the logic of how data is processed in the pipeline. Let's walk through each task in the code to see what it's doing and how it's defined.

First we have the `captech_sql_conn` task:

```python
captech_sql_conn = SnowflakeToLocalOperator(
    task_id='query_snowflake',
    conn_id='CAPTECH_SNOWFLAKE',
    output_path="/opt/airflow/data_files",
    sql_query=sql_query,
    folder_name="{{ ti.task_id }}",
    file_name="{{ data_interval_end }}"
)
```
- This task performs `sql_query` against the Snowflake connection established in `snowflake_to_local.py`, using snowflake hooks, before dumping the results to `output_path/folder_name/file_name` which in our case is within this repo under `data_files`.
- The `sql_query` parameter references a predefined SQL query to perform against the Snowflake connection.
- Reference: `snowflake_to_local.py`


Next we have `feature_engineering`:

```python
feature_engineering = DockerOperator(
    task_id="feature_engineering",
    api_version="auto",
    image="captech-airflow-sandbox-python:0.0.1",
    mount_tmp_dir=False,
    mounts=[
        Mount(source=f"/home/{user}/airflow-sandbox", target="/opt/airflow/", type="bind")
    ],
    environment={
                "task_id": "{{ ti.task_id }}"
    },
    command="python3 opt/airflow/dags/scripts/feature_engineering.py --upstream_task {{ ti.task.upstream_task_ids.pop() }} --filename {{data_interval_end}}.csv",
    dag=dag
)
```
- This task runs `command` in our container to pass the previous file to our `feature_engineering.py` script before some processing takes place there.


Next we have `training`:

```python
training = DockerOperator(
    task_id="training",
    api_version="auto",
    image="captech-airflow-sandbox-python:0.0.1",
    mount_tmp_dir=False,
    mounts=[
        Mount(source=f"/home/{user}/airflow-sandbox", target="/opt/airflow/", type="bind")
    ],
    environment={
                "task_id": "{{ ti.task_id }}"
    },
    command="python3 opt/airflow/dags/scripts/training.py --upstream_task {{ ti.task.upstream_task_ids.pop() }} --filename {{data_interval_end}}.csv",
    dag=dag,
    xcom_all=True
)
```
- This task runs `command` in our container to pass the previous file to our `training.py` script.

Finally we have `write_it` which writes stuff:

```python
write_it = LocalToSnowflake(
    task_id="write_stuff",
    destination_schema="F1",
    destination_table="F1_Predictions",
    conn_id="CAPTECH_SNOWFLAKE",
    folder_name="training",
    file_name="{{ti.xcom_pull(task_ids='training', key='file_name')}}"
)
```
- This task writes `file_name` to the `destination_schema.destination_table`. It adds an `insert_timestamp`field to record the time of writing. 
- Reference: `local_to_snowflake.py`

In the end, the DAG is outlined as follows:

```python
captech_sql_conn >> feature_engineering # first_task >> second_task
feature_engineering >> training # second_task >> third_task
training >> write_it # third_task >> second_task
```

Each task in the DAG builds on the previous, the `>>` python operator helps declare individual task dependencies. 

All of these tasks can be reconfigured with your own data, while building this sandbox the team utilized Formula 1 racing data to predict qualifying times based on various other factors. If you're interested in working with your own data, after storing it in Snowflake and refactoring `sql_query`, editing the `training.py` and `feature_engineering.py` scripts is a good place to start.

Reference: https://airflow.apache.org/docs/apache-airflow/stable/core-concepts/dags.html

**need to add screenshots**


## Configuration and experimentation

**add experimentation, thinking ill walk through what it would look like to edit the demo dag/files to work with diff data OR outline what setting up the F1 stuff looked like** 
