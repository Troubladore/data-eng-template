# Kerberos Authentication - {{cookiecutter.project_name}}

{% if cookiecutter.enable_kerberos == "yes" %}
**Status**: ENABLED - Kerberos authentication is configured for this project.

## What

Kerberos authentication integration for secure access to enterprise data sources requiring Active Directory authentication.

## Why

- **Enterprise Security**: Required for accessing corporate SQL Server, Hadoop, and other Kerberos-secured systems
- **Single Sign-On**: Seamless authentication without storing credentials
- **Compliance**: Meet enterprise security policies and audit requirements

## How

### Development Environment

The development environment uses a **sidecar container** pattern for Kerberos ticket management:

```yaml
# From DEV-compose-sidecar.snippet.yml
services:
  kerberos-sidecar:
    image: kerberos-client:latest
    volumes:
      - kerberos-tickets:/tmp/krb5cc
    environment:
      - KRB5_PRINCIPAL=user@DOMAIN.COM
      - KRB5_KEYTAB=/etc/keytabs/user.keytab
```

**Usage in Development:**
1. Copy `DEV-compose-sidecar.snippet.yml` content into your `docker-compose.override.yml`
2. Configure your keytab files and principal information
3. Kerberos tickets are shared via volume mount to Airflow containers

### Production Environment (Kubernetes)

Production uses **sidecar pod injection** for ticket renewal:

```yaml
# From K8S-sidecar-patch.snippet.yaml
spec:
  containers:
  - name: kerberos-sidecar
    image: kerberos-client:latest
    env:
    - name: KRB5_PRINCIPAL
      value: "svc-airflow@DOMAIN.COM"
    volumeMounts:
    - name: krb5-tickets
      mountPath: /tmp/krb5cc
```

**Production Deployment:**
1. Service account with appropriate Kerberos principals
2. Automatic ticket renewal via init containers and sidecars  
3. Secure keytab management through Kubernetes secrets

## Configuration Files

- `DEV-compose-sidecar.snippet.yml`: Docker Compose sidecar configuration for local development
- `K8S-sidecar-patch.snippet.yaml`: Kubernetes patch for sidecar injection in production

## Environment Variables

Set these in your environment-specific configurations:

```bash
# Development (.env)
KRB5_PRINCIPAL=your-dev-user@DOMAIN.COM
KRB5_REALM=DOMAIN.COM
KRB5_KDC=kdc.domain.com

# Production (Kubernetes secrets)
KRB5_PRINCIPAL: svc-airflow@DOMAIN.COM
KRB5_KEYTAB_SECRET: airflow-keytab
```

## Integration Examples

### SQL Server with Kerberos

```python
from airflow.providers.microsoft.mssql.operators.mssql import MsSqlOperator

sql_task = MsSqlOperator(
    task_id='query_with_kerberos',
    mssql_conn_id='mssql_kerb_connection',  # Uses Kerberos authentication
    sql='SELECT * FROM secure_table',
    dag=dag
)
```

### Hadoop/Hive Access

```python  
from airflow.providers.apache.hive.operators.hive import HiveOperator

hive_task = HiveOperator(
    task_id='hive_query',
    hql='SELECT * FROM secure_hive_table',
    hive_cli_conn_id='hive_kerb_connection',
    dag=dag
)
```

## Troubleshooting

### Common Issues
1. **Ticket Expiration**: Ensure automatic renewal is configured
2. **Clock Skew**: Verify time synchronization between containers and KDC
3. **Network Connectivity**: Confirm KDC accessibility from containers
4. **Principal/Keytab Mismatch**: Validate service principal configuration

### Debug Commands

```bash
# Check ticket status
klist

# Test Kerberos authentication
kinit user@DOMAIN.COM

# Verify service principal
kvno HTTP/service.domain.com
```

## Security Considerations

- **Keytab Security**: Store keytabs in secure secret management (Azure Key Vault, etc.)
- **Principal Rotation**: Regular rotation of service principal credentials
- **Network Security**: Ensure encrypted communication with KDC
- **Audit Logging**: Enable Kerberos audit logging for compliance

{% else %}
**Status**: DISABLED - Kerberos authentication is not enabled for this project.

## What

Kerberos authentication would provide secure access to enterprise data sources requiring Active Directory authentication.

## Why Disabled

This project is configured without Kerberos integration, typically for:
- **Cloud-First Architecture**: Using cloud-native authentication (managed identities, service principals)
- **Development/Testing**: Simplified setup for non-production environments  
- **Different Auth Strategy**: OAuth, API keys, or certificate-based authentication instead

## Enabling Kerberos

To enable Kerberos authentication:

1. **Regenerate Template**: Re-run cookiecutter with `enable_kerberos=yes`
2. **Manual Integration**: Copy configuration from `kerberos/` examples
3. **Update Connections**: Configure Airflow connections to use Kerberos authentication

## Alternative Authentication

Consider these alternatives for secure data access:

- **Managed Identities**: Azure/AWS managed service identities
- **Service Principals**: OAuth 2.0 with certificate or secret authentication
- **API Keys**: Secure API token management via secret stores  
- **Certificate-Based**: X.509 certificates for mutual TLS authentication

{% endif %}