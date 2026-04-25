.PHONY: install test run db-apply

install:
	pip install -e ".[dev]"

test:
	pytest -q

run:
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

db-apply:
	@if [ -z "$$DATABASE_URL" ]; then echo "DATABASE_URL is required"; exit 1; fi
	psql "$$DATABASE_URL" -f supabase/schema.sql
	psql "$$DATABASE_URL" -f supabase/rls-policies.sql
