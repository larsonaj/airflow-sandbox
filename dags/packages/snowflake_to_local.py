from airflow.models.baseoperator import BaseOperator
from airflow.providers.snowflake.hooks.snowflake import SnowflakeHook
from airflow.providers.common.sql.hooks.sql import fetch_all_handler
import snowflake.connector
import pandas as pd
import os



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
        
        # hook = SnowflakeHook(snowflake_conn_id=self.conn_id)

        stmt = self.sql_query


        ctx=snowflake.connector.connect(
          host="captech_partner.us-east-1.snowflakecomputing.com",
          user="",
          password="",
          account="captech_partner",
          warehouse="XS_WH",
          database="TEST_DB",
          schema="DBT_ALARSON",
          protocol='https',
          port=443)


          # Create a cursor object.
        cur = ctx.cursor()

        # Execute a statement that will generate a result set.
        cur.execute(stmt)

        # Fetch the result set from the cursor and deliver it as the Pandas DataFrame.
        data = cur.fetch_pandas_all()

        # query = hook.run(stmt, handler=fetch_pandas_all)

        # data = pd.DataFrame(df)

        os.makedirs(f"{self.output_path}/{self.folder_name}/", exist_ok=True)

        if self.format == "csv":

            data.to_csv(f"{self.output_path}/{self.folder_name}/{self.file_name}.csv", index=False, header=True)

        if self.format == "parquet":

            data.to_parquet(f"{self.output_path}/{self.folder_name}/{self.file_name}.parquet", index=False, header=True)




