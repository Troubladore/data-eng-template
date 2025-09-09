# Airflow DAG Development Guidance

**Context**: Airflow DAGs for {{cookiecutter.project_name}} using medallion architecture with dependency isolation.

## DAG Organization

- **bronze_*.py**: Data ingestion from external sources
- **silver_*.py**: Data cleaning and validation transformations  
- **gold_*.py**: Business metrics and aggregations

## Development Environment

- **Airflow version**: {{cookiecutter.airflow_version}}
- **Executor**: {{cookiecutter.airflow_executor}}
- **Author**: {{cookiecutter.author_name}}

## Modern Airflow 3.0+ Unified Environment

This project leverages **Airflow 3.0.6** with **unified dependency support**, eliminating the need for complex dependency isolation:

### Unified Environment Benefits

- **SQLAlchemy 2.0+ Support**: Both Airflow core and data processing tasks use modern SQLAlchemy
- **Simplified Development**: No environment switching or isolation complexity
- **Modern Database Drivers**: psycopg3 with full SQLAlchemy 2.0+ integration
- **Performance Improvements**: Latest data processing libraries (Polars, Pandas 2.0+)

### Migration from Legacy Approaches

If upgrading from older Airflow versions with dependency isolation:

```python
# OLD (Airflow 2.x with isolation)
from dags.utils.isolated_execution import create_isolated_task
task = create_isolated_task(task_id='process', python_callable=func, dag=dag)

# NEW (Airflow 3.0+ unified)
from airflow.operators.python import PythonOperator
task = PythonOperator(task_id='process', python_callable=func, dag=dag)
```

### Modern SQLAlchemy 2.0+ Usage

```python
def modern_data_processing():
    from sqlalchemy import create_engine, text, MetaData, Table, Column
    
    # Modern connection string with psycopg3
    engine = create_engine("postgresql+psycopg://admin:admin@postgres:5432/db")
    
    with engine.connect() as conn:
        # SQLAlchemy 2.0+ syntax
        result = conn.execute(text("SELECT * FROM table"))
        # Modern table operations, etc.
```

## Best Practices

- Use dataset dependencies between layers
- Implement proper error handling and retries
- Follow naming convention: `{layer}_{source}_{domain}_pipeline`
- **Leverage modern SQLAlchemy 2.0+ features throughout**
- **Use standard PythonOperator for all tasks**
- Test DAGs thoroughly before deployment

See `example_modern_airflow.py` for a complete working example with modern Airflow 3.0+ and SQLAlchemy 2.0+.

## Historical Context: SQLAlchemy Version Conflicts (Solved)

**Reference**: This template previously addressed SQLAlchemy version conflicts that were common in Airflow 2.x environments.

### The Problem (Historical)

Prior to Airflow 3.0, there was a fundamental dependency conflict:
- **Airflow Core** required SQLAlchemy 1.4.x for compatibility
- **Modern Data Processing** benefited from SQLAlchemy 2.0+ features and performance

This led to complex workarounds like:
- Dependency isolation using `PythonVirtualenvOperator`
- Constraint files: `pip install "apache-airflow[celery]==2.8.1" --constraint "https://raw.githubusercontent.com/apache/airflow/constraints-2.8.1/constraints-3.10.txt"`
- Dual virtual environments within containers

### The Solution (Modern)

**Airflow 3.0.6** eliminates these conflicts by:
- **Native SQLAlchemy 2.0+ Support**: Full compatibility throughout the stack
- **Modern Database Drivers**: psycopg3 with optimal SQLAlchemy 2.0 integration  
- **Unified Architecture**: No need for environment isolation or complex workarounds

### Resources

- [Stack Overflow Discussion](https://stackoverflow.com/questions/76365797/how-do-i-get-airflow-to-work-with-sqlalchemy-2-0-2-when-it-has-a-1-4-48-version) - Legacy version conflict examples
- [Airflow Release Notes](https://airflow.apache.org/docs/apache-airflow/stable/release_notes.html) - Modern 3.0+ improvements
- [Apache Airflow GitHub Issue #28723](https://github.com/apache/airflow/issues/28723) - SQLAlchemy 2.0 deprecation fixes

This template now leverages the modern unified approach, eliminating historical complexity while providing access to the latest features and performance improvements.

---

For detailed patterns and examples, see the full `CLAUDE_DETAILED.md` file in this directory.