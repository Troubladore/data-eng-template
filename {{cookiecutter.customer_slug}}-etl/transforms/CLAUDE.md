# SQLModel and Pydantic Data Models for {{cookiecutter.project_name}}

**Context**: Type-safe data validation and API interfaces across medallion architecture.

## Model Organization

- **bronze/**: Raw data models with minimal validation
- **silver/**: Validated business data models with strong typing
- **gold/**: API-ready aggregated models for consumption

## Development Environment

- **Python**: {{cookiecutter.python_version}}
- **Database**: PostgreSQL {{cookiecutter.postgres_version}}
- **Author**: {{cookiecutter.author_name}}

## Key Patterns

- Use SQLModel for database interactions
- Implement Pydantic validators for business rules
- Create type-safe interfaces between pipeline stages

See CLAUDE_DETAILED.md for comprehensive SQLModel patterns and examples.