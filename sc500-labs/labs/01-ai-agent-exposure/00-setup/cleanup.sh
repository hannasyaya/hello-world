#!/usr/bin/env bash
# SC-500 Lab - removes everything that deploy-lab-resources.sh created.
set -euo pipefail
RG="rg-sc500-agents-lab"

KVS="$(az keyvault list -g "$RG" --query '[].name' -o tsv 2>/dev/null || true)"
echo ">> Deleting resource group $RG"
az group delete -n "$RG" --yes
for kv in $KVS; do
  echo ">> Purging soft-deleted Key Vault $kv"
  az keyvault purge -n "$kv" || true
done
echo "Done. If you enabled Defender CSPM only for this lab, turn it off with:"
echo "  az security pricing create -n CloudPosture --tier free"
