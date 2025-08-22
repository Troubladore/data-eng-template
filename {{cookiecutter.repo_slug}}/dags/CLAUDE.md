# Airflow DAG Development Guidance

**Context**: Airflow DAGs for {{cookiecutter.project_name}} using medallion architecture.

## DAG Organization

- **bronze_*.py**: Data ingestion from external sources
- **silver_*.py**: Data cleaning and validation transformations  
- **gold_*.py**: Business metrics and aggregations

## Development Environment

- **Airflow version**: {{cookiecutter.airflow_version}}
- **Executor**: {{cookiecutter.airflow_executor}}
- **Author**: {{cookiecutter.author_name}}

## Best Practices

- Use dataset dependencies between layers
- Implement proper error handling and retries
- Follow naming convention: `{layer}_{source}_{domain}_pipeline`
- Test DAGs thoroughly before deployment

For detailed patterns and examples, see the full `CLAUDE_DETAILED.md` file in this directory.