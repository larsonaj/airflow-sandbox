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
from packages.local_to_snowflake import LocalToSnowflake

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
    select top 10 ORDER_ID, 
    CUSTOMER_ID, 
    cast(ORDER_DATE as varchar) as poop,
    STATUS,
    CREDIT_CARD_AMOUNT,
    COUPON_AMOUNT,
    BANK_TRANSFER_AMOUNT,
    GIFT_CARD_AMOUNT,
    AMOUNT
    from ORDERS
    """

    with open('/opt/airflow/dags/config.yaml') as f:
        config = yaml.safe_load(f)

    captech_sql_conn = SnowflakeToLocalOperator(
        task_id='query_snowflake',
        conn_id='CAPTECH_SNOWFLAKE',
        output_path="/opt/airflow/data_files",
        sql_query=sql_query,
        folder_name="{{ ti.task_id }}",
        file_name="{{ ds }}"
    )

    ls_view = BashOperator(
        task_id="ls",
        bash_command="ls /opt/airflow/dags",
        dag=dag
    )

    t_print = DockerOperator(
        task_id="print",
        api_version="auto",
        image="captech-airflow-sandbox-python:0.0.1",
        mount_tmp_dir=False,
        mounts=[
            Mount(source="/home/jwang/airflow-sandbox", target="/opt/airflow/", type="bind")
        ],
        command=f"python3 opt/airflow/dags/scripts/transform.py",
        dag=dag
    )
    
    write_it = LocalToSnowflake(
        destination_schema="F1",
        destination_table="F1_Predictions",
        conn_id="CAPTECH_SNOWFLAKE",
        folder_name="query_snowflake",
        file_name=xcom_pull(),
    )

    captech_sql_conn
    ls_view
    t_print
