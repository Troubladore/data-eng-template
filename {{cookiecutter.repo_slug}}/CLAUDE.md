# {{cookiecutter.project_name}} - Data Engineering Project

**Generated from data-eng-template**: This is a modern data engineering project with Airflow, dbt, PostgreSQL, and DevContainer using medallion architecture.

---

## Project Structure

- **dags/**: Airflow DAG definitions (see `dags/CLAUDE.md` for specific guidance)
- **dbt/**: Data modeling and transformations (see `dbt/CLAUDE.md`)  
- **transforms/**: SQLModel/Pydantic data models (see `transforms/CLAUDE.md`)
- **scripts/**: Helper utilities and operations (see `scripts/CLAUDE.md`)

## Medallion Architecture

- **Bronze Layer**: Raw data ingestion with minimal processing
- **Silver Layer**: Cleaned, validated, and conformed data  
- **Gold Layer**: Business-ready aggregations and metrics

## Development Environment

- **Airflow UI**: http://localhost:8080 (admin/admin)
- **Database**: PostgreSQL on localhost:5432
- **Author**: {{cookiecutter.author_name}}

## Layer-Specific Guidance

Each directory contains detailed CLAUDE.md files with specific guidance for that layer:

- See `dags/CLAUDE.md` for Airflow DAG patterns
- See `dbt/CLAUDE.md` for data modeling guidance
- See `transforms/CLAUDE.md` for SQLModel patterns
- See `scripts/CLAUDE.md` for operational utilities

This distributed guidance approach provides contextual AI assistance exactly where developers need it.