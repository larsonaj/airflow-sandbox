from airflow.models.baseoperator import BaseOperator
from airflow.providers.snowflake.hooks.snowflake import SnowflakeHook
from snowflake.connector.pandas_tools import write_pandas
import pandas as pd
import os
import csv
from datetime import datetime as dt



class LocalToSnowflake(BaseOperator):

    template_fields = ("file_name", "folder_name")
    
    def __init__(
        self,
        destination_schema,
        destination_table,
        conn_id,
        folder_name,
        file_name,
        mode="insert",
        format="csv",
        **kwargs
    ) -> None:
        super().__init__(**kwargs)
        self.mode = mode
        self.destination_schema=destination_schema
        self.destination_table=destination_table
        self.format = format
        self.folder_name = folder_name
        self.file_name = file_name
        self.conn_id = conn_id



    def execute(self, context):
        # read file into memory

        if format == "parquet":
            df = pd.read_parquet()

        if format == "csv":
            df = pd.read_csv(f'/{self.output_path}/{self.folder_name}/{self.file_name}.csv')
            ## add insert timestamp
            df["insert_timestamp"] = dt.now()

        # build snowflake hook
        hook = SnowflakeHook(snowflake_conn_id=self.conn_id)

        connection=hook.get_conn()


        # generate insert statement

        if mode == "insert":
            success, nchunks, nrows, _ = write_pandas(conn=connection, df=df, table_name=destination_table, schema=destination_schema, database="TEST_DB", quote_identifiers=False)
            print(f"Status: {success}, Chunks: {nchunks}, Rows: {nrows}, Other Stuff: {_}")
        elif mode == "upsert":
            kwargs['primary_key']

        
