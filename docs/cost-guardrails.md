# Azure cost guardrails — verify before provisioning

The $30/month is a target, not a strict Azure cap. Do not create a billable resource without reviewing the specific SKU, region, subscription offer, required companion services, and billing settings.

| Component | Initial choice | Caveat |
|---|---|---|
| Public existing marketing website | GitHub Pages | Leave as-is; no migration cost required |
| Portal frontend | Azure Static Web Apps Free | Development use; free plan quotas and feature limits |
| API | Azure Container Apps Consumption, min replicas 0 | Verify plan, environment, ingress, and any workspace/log ingestion charges |
| Data | Azure SQL Database free tier if subscription eligible | 100k vCore-seconds, 32 GB each data and backup monthly; choose auto-pause when free allowance exhausted |
| Ops monitor | Application Insights and Action Groups, email first | Telemetry/log ingestion and alert rules can cost money; set retention/sampling and monitor spend |
| Event notifications | Start with owner email | Outbound SMS/phone and email services can have usage, number, registration and compliance costs |
| AI | Disabled for first deployment | Test with limited prompts; costs vary by model and usage |

Do not provision dedicated Container Apps workload profiles, always-ready Functions, premium hosting, private endpoints, NAT gateways or SMS phone-number subscriptions without a cost review.

Azure portal path: **Cost Management + Billing -> Cost Management -> Budgets**. Create a monthly budget $30 and email thresholds at 50% and 80% (and optionally 100%). Azure budgets alert you, but usually do **not** stop spend automatically.
