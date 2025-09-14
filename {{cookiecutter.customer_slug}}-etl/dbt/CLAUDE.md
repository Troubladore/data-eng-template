# dbt Modeling Guidance for {{cookiecutter.project_name}}

**Context**: dbt data transformations using medallion architecture.

## Model Organization

- **models/bronze/**: Raw data models (1:1 with sources)
- **models/silver/**: Cleaned and validated data models
- **models/gold/**: Business-ready aggregations and metrics

## Development Environment

- **Database**: PostgreSQL {{cookiecutter.postgres_version}}
- **Python**: {{cookiecutter.python_version}}
- **Author**: {{cookiecutter.author_name}}

## Naming Conventions

- Bronze: `_bronze__source__table`
- Silver: `_silver__domain__entity`
- Gold: `_gold__business__metric`

See CLAUDE_DETAILED.md for comprehensive dbt patterns and examples.