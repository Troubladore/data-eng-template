from datetime import datetime
from airflow import DAG
from airflow.operators.python import PythonOperator

def hello():
    print("Hello from Airflow + Postgres via Podman!")

with DAG(
    dag_id="example_hello",
    start_date=datetime(2024, 1, 1),
    schedule="@daily",
    catchup=False,
    tags=["example"],
):
    PythonOperator(task_id="say_hello", python_callable=hello)
