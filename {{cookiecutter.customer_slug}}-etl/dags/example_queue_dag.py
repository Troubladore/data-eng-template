from airflow import DAG
from airflow.utils.dates import days_ago
from airflow.operators.bash import BashOperator

with DAG(
    dag_id="example_queue_dag",
    start_date=days_ago(1),
    schedule=None,
    tags=["demo","queues"],
):
    BashOperator(
        task_id="light_task",
        bash_command="echo hello from default",
        queue="default"
    )

    BashOperator(
        task_id="mssql_heavy_task",
        bash_command="echo heavy task",
        queue="mssql-kerb"
    )
