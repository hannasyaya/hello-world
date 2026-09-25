#!/usr/bin/env bash
# SC-500 Lab - deploys the Azure resources behind the "DevOps Copilot" and
# "Invoice Processing Agent" scenario. The permissions are too broad on purpose,
# so that Exposure Management has blast radius and attack paths to show.
#
# Use a LAB subscription only. Run cleanup.sh when you finish.
#
# Usage:  ./deploy-lab-resources.sh [--location eastus] [--enable-defender-cspm]
set -euo pipefail

LOCATION="eastus"
ENABLE_CSPM="false"
while [[ $# -gt 0 ]]; do
  case "$1" in
    --location) LOCATION="$2"; shift 2 ;;
    --enable-defender-cspm) ENABLE_CSPM="true"; shift ;;
    *) echo "Unknown argument: $1" >&2; exit 1 ;;
  esac
done

SUFFIX="$(tr -dc 'a-z0-9' </dev/urandom | head -c 5)"
RG="rg-sc500-agents-lab"
KV="kv-sc500ops-${SUFFIX}"
ST="stsc500payroll${SUFFIX}"
MI_DEVOPS="mi-agent-devops"
MI_INVOICE="mi-agent-invoice"

SUB_ID="$(az account show --query id -o tsv)"
ME="$(az ad signed-in-user show --query id -o tsv)"
echo ">> Subscription: $(az account show --query name -o tsv) ($SUB_ID)"

echo ">> Resource group"
az group create -n "$RG" -l "$LOCATION" --tags lab=sc500-ai-agents -o none
RG_ID="$(az group show -n "$RG" --query id -o tsv)"

echo ">> Managed identities that the agents use"
az identity create -g "$RG" -n "$MI_DEVOPS" --tags agent="DevOps Copilot" -o none
az identity create -g "$RG" -n "$MI_INVOICE" --tags agent="Invoice Processing Agent" -o none
DEVOPS_PID="$(az identity show -g "$RG" -n "$MI_DEVOPS" --query principalId -o tsv)"
INVOICE_PID="$(az identity show -g "$RG" -n "$MI_INVOICE" --query principalId -o tsv)"

echo ">> Key Vault (RBAC) holding a credential that belongs to another identity"
az keyvault create -g "$RG" -n "$KV" -l "$LOCATION" --enable-rbac-authorization true -o none
KV_ID="$(az keyvault show -n "$KV" --query id -o tsv)"
az role assignment create --assignee-object-id "$ME" --assignee-principal-type User \
  --role "Key Vault Secrets Officer" --scope "$KV_ID" -o none
echo "   waiting 60s for the RBAC assignment to take effect..."
sleep 60
az keyvault secret set --vault-name "$KV" -n "finance-blueprint-client-secret" \
  --value "LAB-ONLY-NOT-A-REAL-SECRET-${SUFFIX}" \
  --tags owner="Finance Agents Blueprint" -o none

echo ">> Storage account holding 'payroll' data"
az storage account create -g "$RG" -n "$ST" -l "$LOCATION" --sku Standard_LRS \
  --allow-blob-public-access false --min-tls-version TLS1_2 -o none
ST_ID="$(az storage account show -g "$RG" -n "$ST" --query id -o tsv)"
az role assignment create --assignee-object-id "$ME" --assignee-principal-type User \
  --role "Storage Blob Data Contributor" --scope "$ST_ID" -o none
sleep 30
az storage container create --account-name "$ST" -n payroll --auth-mode login -o none
printf 'employee,salary\nsample-user,100000\n' > /tmp/sc500-payroll.csv
az storage blob upload --account-name "$ST" -c payroll -n payroll-2026.csv \
  -f /tmp/sc500-payroll.csv --auth-mode login --overwrite -o none
rm -f /tmp/sc500-payroll.csv

echo ">> Over-broad role assignments (the misconfigurations you will find)"
# DevOps Copilot: Contributor on the whole resource group plus read access to vault secrets
az role assignment create --assignee-object-id "$DEVOPS_PID" --assignee-principal-type ServicePrincipal \
  --role "Contributor" --scope "$RG_ID" -o none
az role assignment create --assignee-object-id "$DEVOPS_PID" --assignee-principal-type ServicePrincipal \
  --role "Key Vault Secrets User" --scope "$KV_ID" -o none
# Invoice agent: data-plane read on the payroll storage account (needs only one container)
az role assignment create --assignee-object-id "$INVOICE_PID" --assignee-principal-type ServicePrincipal \
  --role "Storage Blob Data Reader" --scope "$ST_ID" -o none

if [[ "$ENABLE_CSPM" == "true" ]]; then
  echo ">> Enabling the Defender CSPM plan on the subscription (this plan is billed)"
  az security pricing create -n CloudPosture --tier standard -o none
fi

cat <<EOF

Deployment complete.
  Resource group : $RG
  Key Vault      : $KV
  Storage account: $ST
  Identities     : $MI_DEVOPS ($DEVOPS_PID)
                   $MI_INVOICE ($INVOICE_PID)

Next steps (see 00-setup/README.md):
  1. Attach $MI_DEVOPS to your Foundry agent "DevOps Copilot".
  2. Mark $KV and $ST as critical assets in Exposure Management.
  3. Wait up to 24 hours for the exposure graph to update.
EOF
