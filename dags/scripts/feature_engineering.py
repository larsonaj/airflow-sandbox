import pandas as pd
import argparse
import os

print(os.listdir("/opt/airflow/data_files/query_snowflake"))

parser = argparse.ArgumentParser(
                    prog='data_intake',
                    description='Intakes data',
                    epilog='Data')
parser.add_argument('--filename')
parser.add_argument('--upstream_task')
args = parser.parse_args()
print(args.upstream_task)

df = pd.read_csv(f"/opt/airflow/data_files/{args.upstream_task}/{args.filename}")

print(df.head(5))