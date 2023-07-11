import os
import pandas as pd
import numpy as np
import argparse
from datetime import datetime

def qualify_drive(data):
    if data == "\\N":
        return 0
    else:
        return 1

def to_seconds(time):
    if pd.isnull(time):
        return np.nan
    else:
        seconds = (time.minute * 60) + time.second + (time.microsecond * 0.000001)
        return seconds

task_id = os.environ['task_id']
parser = argparse.ArgumentParser(
                    prog='data_intake',
                    description='Intakes data',
                    epilog='Data')
parser.add_argument('--filename')
parser.add_argument('--upstream_task')
args = parser.parse_args()
file = f"/opt/airflow/data_files/{args.upstream_task}/{args.filename}"

df = pd.read_csv(f"/opt/airflow/data_files/{args.upstream_task}/{args.filename}")

df["q1"] = pd.to_datetime(df["q1"], format='%M:%S.%f', errors='coerce')
df["q2"] = pd.to_datetime(df["q2"], format='%M:%S.%f', errors='coerce')
df["q3"] = pd.to_datetime(df["q3"], format='%M:%S.%f', errors='coerce')
df["fastestLapTime"] = pd.to_datetime(df["fastestLapTime"], format='%M:%S.%f', errors='coerce')
df["q2_drive"] = df["q2"].apply(qualify_drive)
df["q3_drive"] = df["q3"].apply(qualify_drive)
df["q1"] = df["q1"].apply(to_seconds)
df["q2"] = df["q2"].apply(to_seconds)
df["q3"] = df["q3"].apply(to_seconds)
df["fastestLapTime"] = df["fastestLapTime"].apply(to_seconds)

output_path = f"/opt/airflow/data_files/{task_id}"
os.makedirs(output_path, exist_ok=True)

file_path = f"{output_path}/{args.filename}"
df.to_csv(file_path)

print(f"Wrote dataframe to: {file_path}")