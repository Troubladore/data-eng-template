.
├── .claude
│   └── settings.local.json
├── CLAUDE.md
├── cookiecutter.json
├── {{cookiecutter.repo_slug}}
│   ├── airflow
│   │   ├── plugins
│   │   └── requirements.txt
│   ├── dags
│   │   └── example_dag.py
│   ├── dbt
│   │   ├── dbt_project.yml
│   │   ├── models
│   │   │   ├── bronze
│   │   │   │   └── bronze_events.sql
│   │   │   ├── gold
│   │   │   │   └── example_gold.sql
│   │   │   └── silver
│   │   │       └── example_silver.sql
│   │   └── profiles-example.yml
│   ├── .devcontainer
│   │   ├── airflow.env
│   │   ├── bootstrap-dev.sh
│   │   ├── clean.sh
│   │   ├── compose.yaml
│   │   ├── devcontainer.json
│   │   ├── postgres.env
│   │   └── post-start.sh
│   ├── docs
│   │   └── directory_structure.md
│   ├── Makefile
│   ├── pyproject.toml
│   ├── scripts
│   │   ├── airflow-cli.sh
│   │   └── psql.sh
│   ├── tests
│   │   └── test_dag_loads.py
│   └── transforms
│       ├── __init__.py
│       ├── models.py
│       └── README.md
├── .gitignore
├── hooks
│   └── post_gen_project.py
├── .python-version
├── README.md
└── .temp
    └── first_run.md

