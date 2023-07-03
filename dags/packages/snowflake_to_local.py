from airflow.models.baseoperator import BaseOperator
from airflow.providers.snowflake.hooks.snowflake import SnowflakeHook
from airflow.providers.common.sql.hooks.sql import fetch_all_handler
import pandas as pd
import os
import csv



class SnowflakeToLocalOperator(BaseOperator):

    template_fields = ("file_name", "folder_name")
    
    def __init__(
        self,
        output_path,
        conn_id,
        sql_query,
        folder_name,
        file_name,
        mode="overwrite",
        format="csv",
        **kwargs
    ) -> None:
        super().__init__(**kwargs)
        self.mode = mode
        self.format = format
        self.output_path = output_path
        self.folder_name = folder_name
        self.file_name = file_name
        self.conn_id = conn_id
        self.sql_query = sql_query


    def execute(self, context):
        
        hook = SnowflakeHook(snowflake_conn_id=self.conn_id)

        connection=hook.get_conn()

        stmt = self.sql_query

        cur = connection.cursor()

        cur.execute(stmt)

        data = cur.fetchall()

        os.makedirs(f"{self.output_path}/{self.folder_name}/", exist_ok=True)

        if self.format == "csv":

            csv_file_path = f'/{self.output_path}/{self.folder_name}/{self.file_name}.csv'

            with open(csv_file_path, 'w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow([i[0] for i in cur.description])  # Write header names
                writer.writerows(data)

        if self.format == "parquet":

            data.to_parquet(f"{self.output_path}/{self.folder_name}/{self.file_name}.parquet", index=False, header=True)

        cur.close()
        connection.close()


