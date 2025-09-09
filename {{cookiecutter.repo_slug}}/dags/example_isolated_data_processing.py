"""
Example DAG showing isolated data processing with modern dependencies.

This demonstrates how to use SQLAlchemy 2.0+ and modern data processing libraries
while keeping Airflow core on SQLAlchemy 1.4.x for stability.

Key Pattern:
- Airflow orchestration uses DockerOperator for isolated execution
- Data processing runs in separate container with modern dependencies
- Clean separation prevents dependency conflicts
"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.providers.docker.operators.docker import DockerOperator
from airflow.operators.python import PythonOperator

default_args = {
    'owner': '{{cookiecutter.author_name}}',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'example_isolated_data_processing',
    default_args=default_args,
    description='Demonstrate isolated data processing with modern SQLAlchemy 2.0+',
    schedule_interval=None,
    catchup=False,
    tags=['example', 'isolated', 'modern-stack', 'sqlalchemy-2.0'],
)


def check_airflow_environment():
    """Verify Airflow environment - should use SQLAlchemy 1.4.x for stability."""
    import sqlalchemy as sa
    import airflow
    
    result = {
        "airflow_version": airflow.__version__,
        "sqlalchemy_version": sa.__version__,
        "environment": "airflow-core"
    }
    
    print(f"Airflow Core Environment: {result}")
    
    # Verify we're using stable SQLAlchemy 1.4.x in Airflow
    if not sa.__version__.startswith('1.4'):
        print(f"⚠️  Expected SQLAlchemy 1.4.x in Airflow core, got {sa.__version__}")
    else:
        print("✅ Airflow using stable SQLAlchemy 1.4.x")
    
    return result


# Task 1: Check Airflow environment (runs in Airflow context)
check_airflow_env = PythonOperator(
    task_id='check_airflow_environment',
    python_callable=check_airflow_environment,
    dag=dag,
)

# Task 2: Modern data processing (runs in isolated container)
modern_data_processing = DockerOperator(
    task_id='isolated_modern_data_processing',
    image='{{cookiecutter.repo_slug}}-data-processing',
    container_name='modern_data_processing_{% raw %}{{dag.dag_id}}_{{ts_nodash}}{% endraw %}',
    api_version='auto',
    auto_remove=True,
    command=[
        'python', '-c', '''
import sqlalchemy as sa
import pandas as pd
import polars as pl
from sqlalchemy import create_engine, text, MetaData, Table, Column, Integer, String, DateTime
from datetime import datetime
import sys

print("🚀 Modern Data Processing Environment")
print(f"   SQLAlchemy: {sa.__version__}")
print(f"   Pandas: {pd.__version__}")
print(f"   Polars: {pl.__version__}")

# Verify modern SQLAlchemy 2.0+
if not sa.__version__.startswith("2."):
    print(f"❌ Expected SQLAlchemy 2.x, got {sa.__version__}")
    sys.exit(1)
    
print("✅ Using modern SQLAlchemy 2.0+")

# Example: Create sample data with modern libraries
print("\\n📊 Creating sample data with Polars...")
df = pl.DataFrame({
    "id": range(1, 1001),
    "value": [i * 2.5 for i in range(1, 1001)],
    "category": ["A" if i % 3 == 0 else "B" if i % 3 == 1 else "C" for i in range(1, 1001)],
    "timestamp": [datetime.now() for _ in range(1000)]
})

# Modern aggregations (much faster than pandas for large datasets)
result = df.group_by("category").agg([
    pl.col("value").sum().alias("total_value"),
    pl.col("value").mean().alias("avg_value"),
    pl.col("id").count().alias("count")
])

print("\\n📈 Polars aggregation results:")
print(result)

# Example: Modern SQLAlchemy 2.0 database operations
print("\\n🗄️  Modern SQLAlchemy 2.0 operations...")

# Note: In real usage, you would connect to your actual database
# For demo, we use SQLite to show the pattern
engine = create_engine("sqlite:///tmp/modern_demo.db")

with engine.begin() as conn:
    # Modern SQLAlchemy 2.0 syntax
    conn.execute(text("""
        CREATE TABLE IF NOT EXISTS demo_results (
            id INTEGER PRIMARY KEY,
            category TEXT,
            total_value REAL,
            avg_value REAL,
            count INTEGER,
            processed_at TIMESTAMP
        )
    """))
    
    # Insert aggregated results
    for row in result.iter_rows(named=True):
        conn.execute(text("""
            INSERT INTO demo_results (category, total_value, avg_value, count, processed_at)
            VALUES (:category, :total_value, :avg_value, :count, :processed_at)
        """), {
            "category": row["category"],
            "total_value": row["total_value"], 
            "avg_value": row["avg_value"],
            "count": row["count"],
            "processed_at": datetime.now()
        })

print("✅ Modern data processing completed successfully!")
print("\\n🎯 Key Benefits of Isolation:")
print("   • Airflow core stability (SQLAlchemy 1.4.x)")
print("   • Modern data processing features (SQLAlchemy 2.0+)")
print("   • No dependency conflicts")
print("   • Scalable container-based execution")
'''
    ],
    docker_url='unix://var/run/docker.sock',
    network_mode='bridge',
    dag=dag,
)

# Task 3: Validate results (runs in Airflow context)
def validate_processing_results():
    """Validate that isolated processing completed successfully."""
    print("🔍 Validating isolated data processing results...")
    
    # In real scenarios, you might:
    # - Check database for expected records
    # - Validate file outputs
    # - Verify data quality metrics
    # - Update orchestration metadata
    
    print("✅ Isolated data processing validated")
    return {"validation": "passed", "method": "isolated_container"}


validate_results = PythonOperator(
    task_id='validate_processing_results',
    python_callable=validate_processing_results,
    dag=dag,
)

# Define dependencies
check_airflow_env >> modern_data_processing >> validate_results