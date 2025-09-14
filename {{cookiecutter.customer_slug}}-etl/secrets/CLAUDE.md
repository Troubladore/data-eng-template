# Secrets Management - {{cookiecutter.project_name}}

This directory contains **{{cookiecutter.secrets_strategy}}** configuration for secure secret management in production environments.

## What

Secure secret injection for Airflow connections, variables, and application credentials using enterprise-grade secret management platforms.

## Why

- **Security**: Never store secrets in code or plain-text files
- **Rotation**: Automatic secret rotation without application restarts  
- **Audit**: Complete audit trail of secret access
- **Compliance**: Meet enterprise security and compliance requirements

## How

### Azure Key Vault Integration

```bash
# Configure Azure Key Vault secrets
export AZURE_CLIENT_ID=your-service-principal-id
export AZURE_CLIENT_SECRET=your-service-principal-secret
export AZURE_TENANT_ID=your-tenant-id

# Reference secrets in Airflow connections
# Connection ID: my_db_connection
# URI: ${AKV_SECRET_my_database_connection_string}
```

### External Secrets Operator (Kubernetes)

```yaml
# Example: externalsecret-airflow.yaml
apiVersion: external-secrets.io/v1beta1
kind: ExternalSecret
metadata:
  name: airflow-secrets
spec:
  refreshInterval: 15m
  secretStoreRef:
    name: vault-backend
    kind: SecretStore
  target:
    name: airflow-secrets
    creationPolicy: Owner
  data:
  - secretKey: fernet-key
    remoteRef:
      key: airflow/fernet-key
```

## Environment-Specific Patterns

### Development
- **Local Secrets**: Use `.env.example` patterns for non-sensitive defaults
- **Override Capability**: Local development can override with actual secrets as needed
- **No Production Secrets**: Never commit actual secrets to development configs

### Production  
- **External Provider**: All secrets sourced from {{cookiecutter.secrets_strategy}}
- **Just-in-Time**: Secrets fetched only when needed by running tasks
- **Automatic Rotation**: Support for secret rotation without service interruption

## Configuration Files

- `azure-key-vault/`: Azure Key Vault configuration templates and documentation
- `external-secrets-operator/`: Kubernetes External Secrets Operator manifests
- Each subdirectory contains specific implementation guidance and examples

## Best Practices

1. **Never Commit Secrets**: Use this directory for configuration templates only
2. **Environment Separation**: Different secret stores for dev/staging/prod
3. **Least Privilege**: Grant minimum required permissions to service principals
4. **Regular Rotation**: Implement automatic secret rotation schedules
5. **Monitoring**: Set up alerts for secret access failures or anomalies

## Integration with Airflow

Secrets are automatically injected into Airflow via:
- **Connections**: Database and API connection strings
- **Variables**: Configuration values and feature flags  
- **Custom Secrets**: Application-specific credentials and tokens

No code changes required - secrets are resolved at runtime through configured providers.