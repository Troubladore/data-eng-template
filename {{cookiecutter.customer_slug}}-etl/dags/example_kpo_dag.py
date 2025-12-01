from airflow import DAG
from airflow.utils.dates import days_ago
from airflow.providers.cncf.kubernetes.operators.kubernetes_pod import KubernetesPodOperator
from datetime import timedelta

default_args = {"owner": "data-eng", "retries": 1, "retry_delay": timedelta(minutes=5)}

with DAG(
    dag_id="example_kpo_dag",
    default_args=default_args,
    start_date=days_ago(1),
    schedule=None,
    tags=["demo","kpo"],
):
    KubernetesPodOperator(
        task_id="mssql_transform",
        name="mssql-transform",
        image="{{ cookiecutter.image_repo }}:mssql-kerb",
        cmds=["bash","-lc"],
        arguments=["python /app/transform.py"],
        get_logs=True,
        is_delete_operator_pod=True,
    )
