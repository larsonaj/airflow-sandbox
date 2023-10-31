from airflow.models.baseoperator import BaseOperator
from airflow.providers.snowflake.hooks.snowflake import SnowflakeHook
import pandas as pd
from snowflake.connector.pandas_tools import write_pandas


class LocalToSnowflakeOperator(BaseOperator):

    template_fields = ("file_name", "folder_name")
    
    def __init__(
        self,
        table_name,
        conn_id,
        database,
        schema,
        input_path,
        ddl_path,
        folder_name,
        file_name,
        mode="overwrite",
        format="csv",
        **kwargs
    ) -> None:
        super().__init__(**kwargs)
        self.mode = mode
        self.format = format
        self.table_name = table_name
        self.folder_name = folder_name
        self.file_name = file_name
        self.conn_id = conn_id
        self.database = database
        self.schema = schema
        self.input_path = input_path
        self.ddl_path = ddl_path


    def execute(self, context):
       
        hook = SnowflakeHook(snowflake_conn_id=self.conn_id)

        connection=hook.get_conn()

        # open data csv as pandas df
        file_path = f"{self.input_path}/{self.folder_name}/{self.file_name}.csv"
        upload_df = pd.read_csv(file_path)

        cursor = connection.cursor()
        # read ddl sql
        ddl_file = open(self.ddl_path, 'r')
        create_table_sql = ddl_file.read()
        # create table
        cursor.execute(create_table_sql)

        # write df to snowflake
        write_pandas(  
                conn=connection,  
                df=upload_df,  
                table_name=self.table_name.upper(),  
                database=self.database.upper(),  
                schema=self.schema.upper() 
        )
