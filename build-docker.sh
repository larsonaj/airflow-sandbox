docker build airflow_containers -t captech-demo-airflow:0.0.1 --no-cache
docker build dags/docker/python -t captech-airflow-sandbox-python:0.0.1 --no-cache