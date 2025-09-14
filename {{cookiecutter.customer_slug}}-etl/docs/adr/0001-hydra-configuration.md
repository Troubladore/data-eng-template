# ADR 0001: Adopt Hydra for Unified Configuration Management

- **Status**: Accepted
- **Date**: 2025-08-22
- **Author**: {{cookiecutter.author_name}}

## Context

Data engineering projects typically involve complex configuration management across multiple environments (dev/staging/prod), services (database, orchestration, compute), and deployment targets (local, cloud, hybrid).

Traditional approaches have significant limitations:

1. **`.env` files**: Flat key-value pairs become unwieldy with 50+ configuration options
2. **YAML files**: No validation, type safety, or runtime flexibility  
3. **Environment variables**: Difficult to organize hierarchically, no documentation
4. **Config classes**: Hard-coded, require code changes for different environments

### Requirements

- **Type safety** with IDE support and validation
- **Environment management** (dev/staging/prod) with clean overrides
- **Runtime flexibility** - override any setting without editing files
- **Self-documenting** configuration with inline help
- **Hierarchical composition** to avoid duplication
- **Backward compatibility** with Docker Compose and existing tooling

## Decision

We will adopt **Hydra** (https://hydra.cc) as the unified configuration management system for all data engineering template projects.

Hydra provides:

- **Hierarchical configuration** composition from multiple YAML files
- **Command-line overrides** for any configuration parameter
- **Type-safe integration** with Pydantic for validation
- **Environment variable interpolation** for secrets
- **Documentation integration** through inline comments

### Implementation Approach

1. **Configuration Structure**:
   ```
   conf/
   ├── config.yaml              # Main config with defaults
   ├── environment/             # Environment-specific overrides
   ├── database/               # Database configurations
   ├── orchestration/          # Airflow/orchestration settings
   └── local/                  # Local overrides (gitignored)
   ```

2. **Pydantic Integration**:
   ```python
   class Settings(BaseModel):
       project: ProjectSettings
       database: DatabaseSettings
       runtime: RuntimeSettings
   ```

3. **Usage Patterns**:
   ```bash
   # Default configuration
   python scripts/run_pipeline.py
   
   # Environment override
   python scripts/run_pipeline.py environment=prod
   
   # Specific overrides
   python scripts/run_pipeline.py database.host=prod-db.com runtime.parallel_jobs=8
   ```

## Consequences

### Positive

- **Better Developer Experience**: Type-safe configuration with IDE support
- **Environment Consistency**: Clear separation between dev/staging/prod
- **Runtime Flexibility**: No need to edit files for configuration changes
- **Documentation**: Self-documenting configuration with inline comments
- **Validation**: Pydantic catches configuration errors at startup
- **Composition**: Reusable configuration modules across environments

### Negative

- **Learning Curve**: Developers need to learn Hydra concepts
- **Additional Complexity**: More sophisticated than simple .env files
- **Migration Effort**: Existing projects need migration from .env approach
- **Dependency**: Adds Hydra as a required dependency

### Mitigation Strategies

1. **Comprehensive Documentation**: Detailed guides and examples
2. **Migration Tools**: Scripts to convert from .env to Hydra configuration
3. **Fallback Support**: Generate .env files from Hydra for compatibility
4. **Training**: Include Hydra patterns in template examples

## Implementation Plan

### Phase 1: Core Infrastructure ✅
- [x] Set up Hydra configuration structure
- [x] Create Pydantic settings models
- [x] Implement `get_settings()` function
- [x] Update post-generation hook

### Phase 2: Integration ✅  
- [x] Update pipeline runner to use Hydra
- [x] Create environment export script for Docker compatibility
- [x] Update DevContainer setup
- [x] Add comprehensive test coverage

### Phase 3: Documentation ✅
- [x] Create configuration documentation
- [x] Update template documentation
- [x] Add migration guides
- [x] Include usage examples

## Alternatives Considered

### 1. Stick with .env Files
- **Pros**: Simple, widely understood
- **Cons**: No hierarchy, validation, or type safety
- **Decision**: Rejected due to complexity growth in data projects

### 2. Pure YAML Configuration  
- **Pros**: Hierarchical, human-readable
- **Cons**: No validation, type safety, or runtime overrides
- **Decision**: Rejected due to lack of flexibility

### 3. Python Configuration Classes
- **Pros**: Type-safe, programmatic
- **Cons**: Requires code changes for different environments
- **Decision**: Rejected due to inflexibility

### 4. JSON Configuration
- **Pros**: Structured, parseable
- **Cons**: No comments, poor readability, no validation
- **Decision**: Rejected due to poor developer experience

### 5. Dynaconf
- **Pros**: Similar features to Hydra, Python-native
- **Cons**: Less ecosystem support, weaker composition model
- **Decision**: Rejected in favor of Hydra's superior composition

## Success Metrics

1. **Developer Adoption**: >90% of template users successfully configure environments
2. **Configuration Errors**: <5% of deployment issues related to configuration
3. **Developer Experience**: Positive feedback on configuration flexibility
4. **Migration Success**: Existing projects can migrate within 1 day

## References

- [Hydra Documentation](https://hydra.cc/docs/intro/)
- [Pydantic Documentation](https://pydantic.dev/)
- [Template Configuration Guide](../configuration/README.md)
- [Configuration Guide](../configuration/README.md)

## Review Schedule

This ADR will be reviewed in 6 months (2025-02-22) to assess:
- Developer feedback and adoption
- Configuration complexity growth
- Integration challenges discovered
- Alternative solution improvements