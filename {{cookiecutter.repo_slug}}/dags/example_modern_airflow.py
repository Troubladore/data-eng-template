"""
Example DAG demonstrating modern Airflow 3.0+ with SQLAlchemy 2.0+.

This DAG showcases the unified dependency approach possible with Airflow 3.0+,
where both Airflow core and data processing tasks can use modern SQLAlchemy 2.0+.
"""

from datetime import datetime, timedelta
from airflow import DAG
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
    'example_modern_airflow',
    default_args=default_args,
    description='Demonstrate modern Airflow 3.0+ with SQLAlchemy 2.0+',
    schedule_interval=None,  # Manual trigger only
    catchup=False,
    tags=['example', 'modern', 'airflow-3.0', 'sqlalchemy-2.0'],
)


def check_modern_environment():
    """Check the modern Airflow 3.0+ environment - should use SQLAlchemy 2.0+."""
    import sqlalchemy as sa
    import airflow
    import sys
    
    result = {
        "airflow_version": airflow.__version__,
        "python_executable": sys.executable,
        "sqlalchemy_version": sa.__version__,
        "sqlalchemy_major_version": int(sa.__version__.split('.')[0])
    }
    
    print(f"Modern Airflow Environment: {result}")
    
    # Verify we're using modern versions
    if result["sqlalchemy_major_version"] < 2:
        raise ValueError(
            f"Expected SQLAlchemy 2.0+ with Airflow 3.0+, got {sa.__version__}"
        )
    
    return result


def process_with_modern_sqlalchemy():
    """Process data using modern SQLAlchemy 2.0+ features unified in Airflow 3.0+."""
    import sqlalchemy as sa
    from sqlalchemy import create_engine, text, MetaData, Table, Column, Integer, String, DateTime
    from datetime import datetime
    import sys
    
    result = {
        "python_executable": sys.executable,
        "sqlalchemy_version": sa.__version__,
        "sqlalchemy_major_version": int(sa.__version__.split('.')[0])
    }
    
    print(f"Processing Environment: {result}")
    
    # Use modern SQLAlchemy 2.0 syntax - unified across Airflow and tasks
    engine = create_engine("postgresql+psycopg://admin:admin@postgres:5432/{{cookiecutter.db_name}}")
    
    with engine.connect() as conn:
        # Modern SQLAlchemy 2.0 syntax with explicit text()
        result_proxy = conn.execute(text("SELECT version()"))
        db_version = result_proxy.fetchone()[0]
        print(f"Database version: {db_version}")
        
        # Create a table using modern declarative approach
        metadata = MetaData()
        modern_test = Table(
            'modern_airflow_test',
            metadata,
            Column('id', Integer, primary_key=True),
            Column('created_at', DateTime, default=datetime.utcnow),
            Column('message', String(255)),
            Column('airflow_version', String(50)),
            Column('sqlalchemy_version', String(50)),
            extend_existing=True
        )
        
        # Create table if not exists
        metadata.create_all(engine, checkfirst=True)
        
        # Insert test data using modern syntax
        conn.execute(
            modern_test.insert().values(
                message="Data processed with unified modern stack",
                airflow_version="{{cookiecutter.airflow_version}}",
                sqlalchemy_version=sa.__version__
            )
        )
        
        conn.commit()
        
        # Query data using modern approach
        results = conn.execute(
            modern_test.select().limit(5)
        ).fetchall()
        
        print(f"Recent records: {len(results)}")
        for row in results:
            print(f"  {row.id}: {row.message} (Airflow: {row.airflow_version})")
    
    return result


def advanced_data_processing():
    """Example of advanced data processing with unified modern libraries."""
    import sqlalchemy as sa
    import pandas as pd
    try:
        import polars as pl
        polars_available = True
    except ImportError:
        polars_available = False
    
    print(f"Unified Environment - SQLAlchemy: {sa.__version__}")
    print(f"Pandas: {pd.__version__}")
    print(f"Polars available: {polars_available}")
    
    # Create sample data with Polars if available, otherwise Pandas
    if polars_available:
        # Create sample data with Polars
        df = pl.DataFrame({
            "id": range(1, 11),
            "value": [i * 2 for i in range(1, 11)],
            "category": ["A" if i % 2 == 0 else "B" for i in range(1, 11)]
        })
        
        # Process with Polars (much faster than Pandas for large datasets)
        result = df.group_by("category").agg(
            pl.col("value").sum().alias("total_value"),
            pl.col("value").mean().alias("avg_value")
        )
        
        print("Polars processing result:")
        print(result)
        
        # Convert to dict for return (Airflow XCom serialization)
        return result.to_pandas().to_dict('records')
    else:
        # Fallback to Pandas
        df = pd.DataFrame({
            "id": range(1, 11),
            "value": [i * 2 for i in range(1, 11)],
            "category": ["A" if i % 2 == 0 else "B" for i in range(1, 11)]
        })
        
        result = df.groupby("category")["value"].agg(["sum", "mean"]).reset_index()
        print("Pandas processing result:")
        print(result)
        
        return result.to_dict('records')


# Task 1: Check modern Airflow environment - unified dependencies
check_environment = PythonOperator(
    task_id='check_modern_environment',
    python_callable=check_modern_environment,
    dag=dag,
)

# Task 2: Process data with modern SQLAlchemy - no isolation needed
process_data = PythonOperator(
    task_id='process_with_modern_sqlalchemy',
    python_callable=process_with_modern_sqlalchemy,
    dag=dag,
)

# Task 3: Advanced data processing - all in the same unified environment
advanced_processing = PythonOperator(
    task_id='advanced_data_processing',
    python_callable=advanced_data_processing,
    dag=dag,
)

# Define task dependencies - simple linear flow
check_environment >> process_data >> advanced_processing