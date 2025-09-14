# Airflow Plugins - {{cookiecutter.project_name}}

This directory contains **custom Airflow plugins** for extending Airflow functionality with operators, hooks, sensors, and macros.

## What

Custom plugins that extend Airflow's built-in functionality with project-specific operators, hooks, sensors, executors, and macros.

## Why

- **Custom Logic**: Implement business-specific operators and sensors
- **Reusability**: Share common functionality across multiple DAGs
- **Integration**: Connect with proprietary systems and APIs
- **Performance**: Optimize data processing with custom executors

## Plugin Structure

```
airflow/plugins/
├── operators/          # Custom operators
├── hooks/             # Custom hooks for external systems
├── sensors/           # Custom sensors for monitoring
├── macros/            # Custom Jinja2 macros
└── executors/         # Custom executors (rare)
```

## Example Custom Operator

```python
# plugins/operators/custom_operator.py
from airflow.models import BaseOperator
from airflow.utils.decorators import apply_defaults

class CustomDataOperator(BaseOperator):
    """Custom operator for {{cookiecutter.project_name}} data processing."""
    
    @apply_defaults
    def __init__(self, config_path: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.config_path = config_path
    
    def execute(self, context):
        # Custom logic here
        self.log.info(f"Processing with config: {self.config_path}")
```

## Usage in DAGs

```python
from airflow.plugins_manager import AirflowPlugin
from plugins.operators.custom_operator import CustomDataOperator

# In your DAG
custom_task = CustomDataOperator(
    task_id='custom_processing',
    config_path='/opt/airflow/conf/processing.yaml',
    dag=dag
)
```

## Best Practices

1. **Namespace**: Use descriptive names to avoid conflicts
2. **Documentation**: Document all custom components thoroughly
3. **Testing**: Include unit tests for custom plugins
4. **Logging**: Use proper logging for debugging
5. **Configuration**: Use Hydra config system for plugin settings

## Plugin Registration

Plugins are automatically discovered by Airflow. Create a plugin class:

```python
# plugins/my_plugin.py
class MyCustomPlugin(AirflowPlugin):
    name = "{{cookiecutter.customer_slug}}_plugin"
    operators = [CustomDataOperator]
    hooks = [CustomHook]
    sensors = [CustomSensor]
```

This directory starts empty - add plugins as needed for your {{cookiecutter.project_name}} workflows.