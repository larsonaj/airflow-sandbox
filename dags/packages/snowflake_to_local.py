from airflow.models.baseoperator import BaseOperator
from airflow.providers.snowflake.hooks.snowflake import SnowflakeHook
from airflow.providers.common.sql.hooks.sql import fetch_all_handler
import pandas as pd



class SnowflakeToLocalOperator(BaseOperator):
    
    def __init__(
        self,
        output_path,
        conn_id,
        sql_query,
        mode="overwrite",
        format="csv",
        **kwargs
    ) -> None:
        super().__init__(**kwargs)
        self.mode = mode
        self.format = format
        self.output_path = output_path
        self.conn_id = conn_id
        self.sql_query = sql_query


    def execute(self, context):
        
        hook = SnowflakeHook(snowflake_conn_id=self.conn_id)

        stmt = self.sql_query

        query = hook.run(stmt, handler=fetch_all_handler)

        data = pd.DataFrame(query)

        data.to_csv(f"{self.output_path}/file.csv")

        # if self.mode == "overwrite":

        # if self.mode == "append":

        # if self.format == "csv":

        # if self.format == "parquet":




