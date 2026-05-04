# Medicare AI Lead Engine — operational Makefile.
# Every target is idempotent and safe to re-run.

SHELL := /usr/bin/env bash

.DEFAULT_GOAL := help

.PHONY: help
help:  ## Show this help
	@awk 'BEGIN {FS = ":.*##"} /^[a-zA-Z_-]+:.*##/ {printf "  \033[36m%-22s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

.PHONY: setup
setup:  ## Apply Supabase migrations (requires SUPABASE_DB_URL)
	./scripts/setup.sh

.PHONY: seed
seed:  ## Seed agents/licenses/carriers from onboarding/*.csv
	./scripts/seed-agents.sh \
	  onboarding/agents.csv \
	  onboarding/agent_licenses.csv \
	  onboarding/agent_carrier_appointments.csv

.PHONY: verify
verify:  ## Run preflight verification
	./scripts/verify-deployment.sh

.PHONY: smoke
smoke:  ## Submit a smoke-test lead through the live edge proxy
	./scripts/smoke-lead.sh

.PHONY: cleanup-smoke
cleanup-smoke:  ## Remove smoke leads and dependents
	./scripts/cleanup-smoke.sh

.PHONY: workflows-validate
workflows-validate:  ## Validate all n8n JSON files parse
	@for f in n8n/*.json; do \
	  python3 -c "import json,sys; json.load(open('$$f'))" && echo "OK: $$f" || (echo "FAIL: $$f" && exit 1); \
	done

.PHONY: deploy-workers
deploy-workers:  ## Deploy Cloudflare Workers (requires wrangler login)
	cd workers && wrangler deploy --env lead_capture
	cd workers && wrangler deploy --env twiml_bridge

.PHONY: audit
audit:  ## Run the daily compliance audit on demand
	curl -sS -X POST "$$N8N_BASE_URL/webhook/medicare-daily-audit" \
	  -H "x-internal-token: $$N8N_INTERNAL_TOKEN" -d '{}' | jq .

.PHONY: fmt
fmt:  ## Format SQL + JSON
	@command -v pg_format >/dev/null && for f in supabase/migrations/*.sql; do pg_format -i "$$f"; done || true
	@command -v jq        >/dev/null && for f in n8n/*.json; do jq . "$$f" > "$$f.tmp" && mv "$$f.tmp" "$$f"; done || true
