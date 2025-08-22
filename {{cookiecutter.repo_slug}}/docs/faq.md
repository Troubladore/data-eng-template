# Frequently Asked Questions

Common questions and solutions for {{cookiecutter.project_name}}.

## Configuration

### Q: How do I change the database connection?

**A**: Use Hydra configuration overrides:

```bash
# Command line override
python scripts/run_pipeline.py database.host=new-db.com database.port=5433

# Or create environment-specific configuration
# conf/environment/custom.yaml
database:
  host: "new-db.com"
  port: 5433
```

### Q: What's the difference between .env files and Hydra configuration?

**A**: This project uses **Hydra as the single source of truth** for configuration:

- **Hydra**: Hierarchical, type-safe, documented configuration with runtime overrides
- **.env**: Generated automatically from Hydra for Docker Compose compatibility
- **Never edit .env manually** - it will be overwritten

### Q: How do I add new configuration options?

**A**: 
1. Add to appropriate YAML file in `conf/`
2. Update Pydantic model in `src/*/config/settings.py`
3. Document the new option with inline comments

```yaml
# conf/config.yaml
my_new_setting:
  enabled: true  # Enable my new feature
  threshold: 100  # Processing threshold
```

```python
# settings.py
class MySettings(BaseModel):
    enabled: bool = Field(True, description="Enable my new feature")
    threshold: int = Field(100, description="Processing threshold", ge=1)
```

## Development Environment

### Q: DevContainer won't start, what should I check?

**A**: Common issues and solutions:

1. **Docker not running**: Ensure Docker Desktop is running
2. **Port conflicts**: Check if ports 8080 or 5432 are already in use
3. **Memory**: DevContainer needs ~4GB RAM, recommend 8GB+
4. **Permissions**: On Linux, ensure user ID matches container user

```bash
# Check Docker
docker --version

# Check ports
netstat -an | grep :8080
netstat -an | grep :5432

# Free up memory
docker system prune -f
```

### Q: How do I restart services in DevContainer?

**A**: Restart specific services:

```bash
# Restart all services
docker-compose -f .devcontainer/compose.yaml restart

# Restart specific services
docker-compose -f .devcontainer/compose.yaml restart airflow-webserver
docker-compose -f .devcontainer/compose.yaml restart postgres
```

### Q: Can I use this template without DevContainers?

**A**: Yes! See the [operations guide](operations/README.md):

```bash
# Install dependencies
uv sync

# Generate environment variables
./scripts/export_env.sh > .env

# Start services manually
docker-compose -f .devcontainer/compose.yaml up -d
```

## Pipeline Development

### Q: How do I test my pipeline changes?

**A**: Use dry-run mode and incremental testing:

```bash
# Test configuration changes
python scripts/run_pipeline.py runtime.dry_run=true

# Test with debug logging
python scripts/run_pipeline.py runtime.debug_mode=true runtime.dry_run=true

# Test dbt models
cd dbt
dbt run --models my_model --target dev
dbt test --models my_model
```

### Q: How do I add a new data source?

**A**: Follow the medallion architecture pattern:

1. **Create bronze model** to ingest raw data
2. **Create silver model** to clean and validate
3. **Update gold models** to include new data
4. **Add data quality tests**

```sql
-- models/bronze/bronze_new_source.sql
SELECT 
    *,
    CURRENT_TIMESTAMP as _ingested_at,
    'new_source' as _source_system
FROM {% raw %}{{ source('new_source', 'raw_table') }}{% endraw %}
```

### Q: How do I handle schema changes?

**A**: Use dbt's schema evolution features:

```sql
-- Handle missing columns gracefully
SELECT 
    id,
    name,
    {% raw %}{{ dbt_utils.safe_add(['column_a', 'column_b']) }}{% endraw %} as total,
    {% raw %}{{ dbt_utils.get_column_values(ref('my_table'), 'status_column', default=['active', 'inactive']) }}{% endraw %}
FROM {% raw %}{{ ref('my_table') }}{% endraw %}
```

## Airflow Integration

### Q: How do I access the Airflow UI?

**A**: Once DevContainer is running:
- **URL**: http://localhost:8080
- **Username**: admin
- **Password**: admin

### Q: My DAG isn't showing up in Airflow

**A**: Common causes:

1. **Syntax errors**: Check DAG file for Python syntax issues
2. **Import errors**: Ensure all dependencies are available
3. **File location**: DAGs must be in the `dags/` directory
4. **DAG schedule**: Check if `start_date` is in the past

```bash
# Test DAG syntax
python dags/my_dag.py

# Check Airflow logs
docker-compose -f .devcontainer/compose.yaml logs -f airflow-webserver
```

### Q: How do I schedule my pipeline?

**A**: Configure schedule in your DAG:

```python
dag = DAG(
    'my_pipeline',
    schedule_interval='@daily',  # or cron expression like '0 2 * * *'
    start_date=datetime(2025, 1, 1),
    catchup=False  # Don't backfill historical runs
)
```

## dbt Questions

### Q: How do I run only specific models?

**A**: Use dbt model selection:

```bash
# Run single model
dbt run --models my_model

# Run model and downstream
dbt run --models my_model+

# Run model and upstream  
dbt run --models +my_model

# Run by tag
dbt run --models tag:bronze

# Run by folder
dbt run --models models/silver
```

### Q: How do I test data quality?

**A**: Use built-in dbt tests and custom tests:

```yaml
# models/schema.yml
models:
  - name: my_model
    columns:
      - name: id
        tests:
          - unique
          - not_null
      - name: status
        tests:
          - accepted_values:
              values: ['active', 'inactive', 'pending']
```

```sql
-- tests/assert_valid_dates.sql
SELECT *
FROM {% raw %}{{ ref('my_model') }}{% endraw %}
WHERE created_at > CURRENT_DATE
```

### Q: How do I document my models?

**A**: Add descriptions in schema.yml and use dbt docs:

```yaml
models:
  - name: customer_summary
    description: "Daily customer activity summary with key metrics"
    columns:
      - name: customer_id
        description: "Unique customer identifier"
      - name: total_orders
        description: "Number of orders placed by customer"
```

```bash
# Generate and serve documentation
dbt docs generate
dbt docs serve --port 8081
```

## Deployment

### Q: How do I deploy to production?

**A**: Use production environment configuration:

```bash
# Run with production config
python scripts/run_pipeline.py environment=prod

# Generate production environment variables
./scripts/export_env.sh environment=prod > .env.prod

# Build production container
docker build -t my-project:prod .
```

### Q: How do I manage secrets in production?

**A**: Use environment variable interpolation in Hydra configs:

```yaml
# conf/database/postgres_cloud.yaml
host: "${POSTGRES_HOST}"
user: "${POSTGRES_USER}"
password: "${POSTGRES_PASSWORD}"
```

Then set environment variables in your deployment environment.

### Q: How do I scale the pipeline?

**A**: Adjust parallelism settings:

```bash
# Increase parallel jobs
python scripts/run_pipeline.py runtime.parallel_jobs=16

# Adjust Airflow parallelism
python scripts/run_pipeline.py orchestration.parallelism=32
```

## Troubleshooting

### Q: I'm getting "Permission denied" errors

**A**: Common on Linux systems:

```bash
# Fix DevContainer permissions
sudo chown -R $USER:$USER .

# Fix Docker socket permissions
sudo usermod -aG docker $USER
# Then log out and back in
```

### Q: Database connection fails

**A**: Check configuration and connectivity:

```bash
# Test database connection
./scripts/psql.sh -c "SELECT version();"

# Check configuration
python -c "from my_project.config import get_settings; s=get_settings(); print(s.database.connection_url)"

# Verify services are running
docker-compose -f .devcontainer/compose.yaml ps
```

### Q: Pipeline runs but produces no results

**A**: Enable debug mode and check logs:

```bash
# Run in debug mode
python scripts/run_pipeline.py runtime.debug_mode=true

# Check for dry run mode
python scripts/run_pipeline.py runtime.dry_run=false

# Examine logs
tail -f logs/pipeline.log
```

## Performance

### Q: Pipeline is running slowly

**A**: Profile and optimize:

```bash
# Run with timing
python scripts/run_pipeline.py runtime.debug_mode=true

# Adjust parallelism
python scripts/run_pipeline.py runtime.parallel_jobs=8

# Check dbt performance
cd dbt
dbt run --models my_slow_model --profiles-dir profiles/ --vars '{"limit": 1000}'
```

### Q: Database queries are slow

**A**: Optimize database performance:

```bash
# Check database performance
./scripts/psql.sh -c "SELECT * FROM pg_stat_activity;"

# Run ANALYZE
./scripts/psql.sh -c "ANALYZE;"

# Check indexes
./scripts/psql.sh -c "SELECT * FROM pg_stat_user_indexes WHERE idx_scan = 0;"
```

## Getting Help

### Q: Where can I find more help?

**A**: Resources for additional support:

1. **Documentation**: Browse [`docs/`](.) directory
2. **Examples**: Look at example DAGs and models in the template
3. **Issues**: Check [GitHub issues](https://github.com/your-org/{{cookiecutter.repo_slug}}/issues)
4. **Logs**: Always check application and service logs for error details

### Q: How do I report bugs or request features?

**A**: 
1. **Search existing issues** first
2. **Include configuration** and error messages
3. **Provide steps to reproduce** the issue
4. **Include environment information** (OS, Docker version, etc.)

### Q: Can I contribute improvements?

**A**: Yes! See [CONTRIBUTING.md](../CONTRIBUTING.md) for guidelines on:
- Code style and standards
- Testing requirements  
- Documentation updates
- Pull request process