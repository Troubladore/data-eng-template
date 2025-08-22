# Distributed AI Guidance Strategy

This document describes the implemented distributed guidance approach for the data engineering cookiecutter template, creating an **AI-first, ready-to-work foundation**.

## Strategy Overview

### Problem Solved
- **Single guidance file limitations**: One large CLAUDE.md becomes unwieldy and lacks context-specific guidance
- **Generic advice**: Without layer-specific context, AI assistants provide generic rather than domain-focused help
- **Discovery friction**: Developers working in specific areas (dags/, dbt/, etc.) need immediate, relevant guidance

### Solution: Two-Layer Guidance Distribution

**Outer Layer (Template Repository)**
- **File**: `/CLAUDE.md`
- **Focus**: Cookiecutter template mechanics, DevContainer setup, template development
- **Audience**: Template maintainers and developers working on the template itself

**Inner Layer (Generated Project)**  
- **Files**: Multiple `CLAUDE.md` files distributed throughout project structure
- **Focus**: Domain-specific data engineering patterns and layer-specific guidance
- **Audience**: Data engineers working on the generated project

## Implementation Structure

```
# Template Repository (Outer Layer)
data-eng-template/
├── CLAUDE.md                           # Template development guidance
├── cookiecutter.json                   # Variables with author_name, db_* fields
└── {{cookiecutter.repo_slug}}/         # Generated project structure
    ├── CLAUDE.md                       # Project-level guidance
    ├── dags/CLAUDE.md                  # Airflow DAG patterns
    ├── dbt/CLAUDE.md                   # dbt modeling guidance  
    ├── transforms/CLAUDE.md            # SQLModel/Pydantic patterns
    └── scripts/CLAUDE.md               # Operational utilities guidance

# Generated Project (Inner Layer)
awesome-data-project/
├── CLAUDE.md                           # "Awesome Data Project - Data Engineering Project"
├── dags/CLAUDE.md                      # "Airflow DAG Development Guidance"
├── dbt/CLAUDE.md                       # "dbt Modeling Guidance for Awesome Data Project"
├── transforms/CLAUDE.md                # "SQLModel and Pydantic Data Models"
└── scripts/CLAUDE.md                   # "Helper Scripts for Awesome Data Project"
```

## Content Distribution Strategy

### Outer Layer Content (Template Development)
- Cookiecutter variable management and template structure
- DevContainer configuration and service orchestration
- Template testing and validation strategies  
- Cross-cutting architectural decisions (tool versions, integration patterns)
- File editing workarounds and template-specific issues
- ChatGPT collaboration workflow for template improvements

### Inner Layer Content (Domain-Specific)

**Project Root (`CLAUDE.md`)**
- Project mission and medallion architecture overview
- Development environment setup (Airflow UI, database connections)
- Cross-layer workflow patterns and testing strategies
- Layer navigation guide (pointing to specific CLAUDE.md files)

**DAGs Layer (`dags/CLAUDE.md`)**
- Airflow-specific patterns: DAG organization, naming conventions
- Task group patterns, error handling, and retry logic
- Dataset dependencies and cross-DAG coordination
- Integration with dbt runs and data quality checks

**dbt Layer (`dbt/CLAUDE.md`)**
- Medallion architecture modeling conventions (bronze/silver/gold)
- Naming patterns: `_bronze__source__table`, `_silver__domain__entity`
- SCD Type 2 implementation, incremental model strategies
- Testing patterns and data quality validation

**Transforms Layer (`transforms/CLAUDE.md`)**
- SQLModel and Pydantic patterns for type-safe data validation
- Bronze/Silver/Gold model characteristics and validation levels
- Database integration patterns and performance optimization
- API interface design for data consumption

**Scripts Layer (`scripts/CLAUDE.md`)**
- Operational script standards and error handling patterns
- Development, operations, and maintenance script organization
- Configuration management and logging standardization
- Database utilities and performance monitoring tools

## Key Benefits Achieved

### 1. Contextual AI Assistance
- **Problem**: Generic guidance regardless of working context
- **Solution**: Layer-specific guidance provides relevant context when Claude is asked for help
- **Example**: Working in `dags/` directory gets Airflow-specific patterns, not generic advice

### 2. Scalable Documentation
- **Problem**: Single large file becomes unmaintainable
- **Solution**: Distributed files can be independently maintained and expanded
- **Example**: Adding new dbt patterns only requires updating `dbt/CLAUDE.md`

### 3. Discovery and Navigation
- **Problem**: Finding relevant guidance in large documents
- **Solution**: Guidance co-located with code provides immediate assistance
- **Example**: Developer in `transforms/` directory immediately sees SQLModel guidance

### 4. AI-First Development Experience
- **Problem**: AI assistants lack project-specific context
- **Solution**: Each CLAUDE.md provides full context for stateless AI interactions
- **Example**: Each file includes project variables, tool versions, and domain context

### 5. Template Evolution Support
- **Problem**: Template changes require manual documentation updates
- **Solution**: Cookiecutter variables ensure generated guidance stays current
- **Example**: `{{cookiecutter.airflow_version}}` automatically reflects chosen version

## Implementation Lessons Learned

### 1. Cookiecutter Template Syntax Conflicts
**Challenge**: dbt Jinja syntax (`{{ ref('model') }}`) conflicts with cookiecutter templates
**Solution**: Use `{% raw %}...{% endraw %}` blocks or separate detailed examples into non-templated files

### 2. Variable Completeness
**Challenge**: Missing cookiecutter variables cause generation failures
**Solution**: Comprehensive `cookiecutter.json` with all necessary project variables:
```json
{
  "project_name": "Awesome Data Project",
  "repo_slug": "awesome-data-project", 
  "author_name": "Data Engineering Team",
  "db_name": "{{ cookiecutter.repo_slug.replace('-', '_') }}",
  "db_user": "postgres",
  "db_password": "postgres"
}
```

### 3. Simplicity vs Comprehensiveness
**Challenge**: Balancing detailed guidance with template generation complexity
**Solution**: Start with simplified guidance that works, then add detailed examples separately

### 4. Testing Strategy
**Challenge**: Validating distributed guidance approach
**Solution**: 
- Test cookiecutter generation: `cookiecutter . --no-input`
- Verify all CLAUDE.md files are created with correct variable substitution
- Validate project structure matches intended distribution

## Usage Patterns

### For Template Developers
1. Work in main template directory with outer layer `CLAUDE.md`
2. Focus on cookiecutter mechanics, DevContainer configuration
3. Test template generation frequently
4. Update inner layer guidance when adding new patterns

### For Data Engineers (Generated Project Users)  
1. Start with project root `CLAUDE.md` for overall context
2. Navigate to layer-specific `CLAUDE.md` files when working in specific areas
3. Use layer-specific context when asking Claude for assistance
4. Reference detailed patterns in domain-specific guidance files

### For AI Assistants (Claude)
1. **Template Work**: Use outer layer guidance for cookiecutter, DevContainer, and template concerns
2. **Generated Project Work**: Use inner layer guidance for domain-specific data engineering patterns
3. **Context Awareness**: Each CLAUDE.md provides full stateless context for the specific layer
4. **Navigation**: Follow guidance file references for comprehensive patterns

## Success Metrics

The distributed guidance strategy successfully achieved:

✅ **Template Generation**: Cookiecutter generates projects with complete guidance distribution
✅ **Variable Resolution**: All `{{cookiecutter.*}}` variables properly resolve in generated files  
✅ **Context Separation**: Clear distinction between template and domain concerns
✅ **Layer-Specific Guidance**: Each directory provides relevant, focused assistance
✅ **AI-Ready Foundation**: Generated projects include comprehensive AI interaction context

## Future Enhancements

### 1. Detailed Pattern Libraries
- Create comprehensive `CLAUDE_DETAILED.md` files with escaped dbt syntax
- Include complete code examples and advanced patterns
- Provide industry best practices and troubleshooting guides

### 2. Dynamic Content Generation
- Use cookiecutter hooks to generate layer-specific content based on chosen features
- Customize guidance based on selected tools and configurations
- Include environment-specific deployment guidance

### 3. Interactive Documentation
- Link to external resources and documentation
- Provide runnable examples and quick-start commands
- Include troubleshooting decision trees and diagnostic tools

## Conclusion

The distributed AI guidance strategy transforms the data engineering template from a basic scaffolding tool into a comprehensive **AI-first, ready-to-work foundation**. By separating template concerns from domain expertise and distributing guidance contextually throughout the project structure, developers get immediate, relevant assistance exactly where they need it.

This approach scales with project complexity, supports template evolution, and provides a superior developer experience by embedding professional data engineering patterns directly into the project structure with full AI assistant integration.