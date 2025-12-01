# Template Development & Testing

Documentation for developing and testing the cookiecutter template itself.

## Test the Template

```bash
# Clone template repository
git clone https://github.com/Troubladore/data-eng-template.git
cd data-eng-template

# Setup test environment
uv sync
source .venv/bin/activate

# Run comprehensive test suite
make test                    # All tests
pytest -m unit             # Unit tests only
pytest -m integration      # Integration tests
pytest -m e2e              # End-to-end workflow tests
pytest -m stress           # Concurrent operation stress tests
```

## Cleanup Test Artifacts

```bash
# Remove generated test projects and Docker artifacts
bash tests/utils/cleanup-shallow.sh

# Deep cleanup (removes all template-related Docker artifacts)
bash tests/utils/cleanup-deep.sh
```

## Contributing

1. **Fork the repository**
2. **Create feature branch**: `git checkout -b feature/amazing-feature`
3. **Make changes and test**: `make test`
4. **Commit changes**: `git commit -m 'Add amazing feature'`
5. **Push to branch**: `git push origin feature/amazing-feature`
6. **Create Pull Request**

**Testing Requirements**: All changes must pass the 4-tier test suite (unit/integration/e2e/stress) before merge.