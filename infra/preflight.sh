#!/usr/bin/env bash
set -euo pipefail
# Read-only; this does not create any Azure resources.
SUB="CamGotIT-Lab"
if ! command -v az >/dev/null; then echo 'Azure CLI not installed. Install Azure CLI first.' >&2; exit 1; fi
printf '\n[1] Subscription context (review before proceeding)\n'
az account list --query '[].{Name:name,State:state,Default:isDefault}' --output table
printf '\n[2] Target subscription metadata\n'
az account show --subscription "$SUB" --query '{Name:name,State:state,Tenant:tenantId,Id:id,User:user.name}' --output json
printf '\n[3] Current caller Azure RBAC assignments (may be empty if permissions differ)\n'
USER_ID="$(az ad signed-in-user show --query id -o tsv 2>/dev/null || true)"
if [[ -n "$USER_ID" ]]; then az role assignment list --subscription "$SUB" --assignee "$USER_ID" --query '[].{Role:roleDefinitionName,Scope:scope}' --output table || true; fi
printf '\n[4] Resource provider registration states\n'
for provider in Microsoft.Web Microsoft.App Microsoft.Sql Microsoft.Insights Microsoft.Storage; do
  echo "$provider: $(az provider show --namespace "$provider" --subscription "$SUB" --query registrationState -o tsv 2>/dev/null || echo unavailable)"
done
printf '\nPreflight is read-only. Verify billing offer, free tier, and budgets in the Azure portal before deploying.\n'
