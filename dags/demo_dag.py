#
# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.
"""
This sample "listen to directory". move the new file and print it,
using docker-containers.
The following operators are being used: DockerOperator,
BashOperator & ShortCircuitOperator.
TODO: Review the workflow, change it accordingly to
your environment & enable the code.
"""
from __future__ import annotations

import os
from datetime import datetime

from docker.types import Mount

from airflow import models
from airflow.operators.bash import BashOperator
from airflow.operators.python import ShortCircuitOperator
from airflow.providers.docker.operators.docker import DockerOperator
from airflow.providers.common.sql.operators.sql import SQLExecuteQueryOperator
from airflow.providers.snowflake.operators.snowflake import SnowflakeOperator
from airflow.hooks.base import BaseHook
from packages.snowflake_to_local import SnowflakeToLocalOperator

import yaml

## General pattern to follow
    # Query CT on prem SQL server
        # Stash results in parquet "locally"
    # Use docker container, with data mounted
        # Apply set of transformations of data and construct model
    # Store model artifacts somewhere?


ENV_ID = os.environ.get("SYSTEM_TESTS_ENV_ID")
DAG_ID = "docker_sample_copy_data"

with models.DAG(
    DAG_ID,
    schedule="@once",
    start_date=datetime(2021, 1, 1),
    catchup=False,
    tags=["demo", "sandbox", "Captech"],
) as dag:


    sql_query = """
    select q."q1",
        q."q2",
        q."q3",
        dr."driverId",
        r."year" - year(dr."dob") as age,
        cr."constructorId",
        cr."nationality",
        r."year",
        c."circuitId",
        s."fastestLapTime"
    from F1.QUALIFYING as q
    left join F1.DRIVERS as dr
        on (q."driverId" = dr."driverId")
    left join F1.CONSTRUCTORS as cr
        on (q."constructorId" = cr."constructorId")
    left join F1.RACES r
        on (q."raceId" = r."raceId")
    left join F1.CIRCUITS c
        on (r."circuitId"= c."circuitId")
    left join F1.RESULTS s
        on (q."raceId" = s."raceId")
    """

    with open('/opt/airflow/dags/config.yaml') as f:
        config = yaml.safe_load(f)

    captech_sql_conn = SnowflakeToLocalOperator(
        task_id='query_snowflake',
        conn_id='CAPTECH_SNOWFLAKE',
        output_path="/opt/airflow/data_files",
        sql_query=sql_query,
        folder_name="{{ ti.task_id }}",
        file_name="{{ data_interval_end }}"
    )

    feature_engineering = DockerOperator(
        task_id="feature_engineering",
        api_version="auto",
        image="captech-airflow-sandbox-python:0.0.1",
        mount_tmp_dir=False,
        mounts=[
            Mount(source="/home/jwang/airflow-sandbox", target="/opt/airflow/", type="bind")
        ],
        environment={
                    "task_id": "{{ ti.task_id }}"
        },
        command="python3 opt/airflow/dags/scripts/feature_engineering.py --upstream_task {{ ti.task.upstream_task_ids.pop() }} --filename {{data_interval_end}}.csv",
        dag=dag
    )

    training = DockerOperator(
        task_id="training",
        api_version="auto",
        image="captech-airflow-sandbox-python:0.0.1",
        mount_tmp_dir=False,
        mounts=[
            Mount(source="/home/jwang/airflow-sandbox", target="/opt/airflow/", type="bind")
        ],
        environment={
                    "task_id": "{{ ti.task_id }}"
        },
        command="python3 opt/airflow/dags/scripts/training.py --upstream_task {{ ti.task.upstream_task_ids.pop() }} --filename {{data_interval_end}}.csv",
        dag=dag
    )
    # ## generate SQL hook
    # sql_connection_hook = get_connection(conn_id = FROM_CONFIG)

    # extract = SQLExecuteQueryOperator(
    #     sql = sql_query
    # )

    # t_view = BashOperator(
    #     task_id="view_file",
    #     bash_command=locate_file_cmd,
    #     do_xcom_push=True,
    #     params={"source_location": "/your/input_dir/path"},
    #     dag=dag,
    # )

    # t_is_data_available = ShortCircuitOperator(
    #     task_id="check_if_data_available",
    #     python_callable=lambda task_output: not task_output == "",
    #     op_kwargs=dict(task_output=t_view.output),
    #     dag=dag,
    # )

    # t_move = DockerOperator(
    #     api_version="auto",
    #     docker_url="unix://var/run/docker.sock",  # replace it with swarm/docker endpoint
    #     image="captech/python-processing-container:latest",
    #     network_mode="bridge",
    #     mounts=[
    #         Mount(source="/your/host/input_dir/path", target="/your/input_dir/path", type="bind"),
    #         Mount(source="/your/host/output_dir/path", target="/your/output_dir/path", type="bind"),
    #     ],
    #     command=[
    #         "/bin/bash",
    #         "-c",
    #         "/bin/sleep 30; "
    #         "/bin/mv {{ params.source_location }}/" + str(t_view.output) + " {{ params.target_location }};"
    #         "/bin/echo '{{ params.target_location }}/" + f"{t_view.output}';",
    #     ],
    #     task_id="move_data",
    #     do_xcom_push=True,
    #     params={"source_location": "/your/input_dir/path", "target_location": "/your/output_dir/path"},
    #     dag=dag,
    # )

    # t_print = DockerOperator(
    #     api_version="auto",
    #     docker_url="unix://var/run/docker.sock",
    #     image="captech/python-processing-container:latest",
    #     mounts=[Mount(source="/your/host/output_dir/path", target="/your/output_dir/path", type="bind")],
    #     command=f"cat {t_move.output}",
    #     task_id="print",
    #     dag=dag,
    # )

    # TEST BODY
    captech_sql_conn >> feature_engineering >> training
