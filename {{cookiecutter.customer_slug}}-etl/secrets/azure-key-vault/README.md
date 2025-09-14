# Azure Key Vault with Airflow (Astronomer Software)

Set these env vars on the Deployment:
- AIRFLOW__SECRETS__BACKENDS=airflow.providers.microsoft.azure.secrets.key_vault.AzureKeyVaultBackend
- AIRFLOW__SECRETS__AZURE_KEY_VAULT__VAULT_URL=https://<your-vault>.vault.azure.net/
- AIRFLOW__SECRETS__AZURE_KEY_VAULT__TENANT_ID=<tenant>
- AIRFLOW__SECRETS__AZURE_KEY_VAULT__CLIENT_ID=<appId>
- AIRFLOW__SECRETS__AZURE_KEY_VAULT__CLIENT_SECRET=<secret>
