# AI Agent Governance & Operation Rules (AI Harness)

This repository follows a strict governance model for AI Agents.

## Rule 1: No Unsafe Frontend Tenant Input
- Never accept `organization_id` or `tenant_id` directly from user HTTP requests (POST, GET, JSON body).
- Always resolve current organization strictly from `request.current_organization` injected by authentication middleware.

## Rule 2: Multi-Tenant Query Filtering
- Never fetch tenant-scoped resources by primary key (`id`) alone.
- All database and file queries must explicitly filter by `organization=request.current_organization`.

## Rule 3: Zero Information Leakage
- Never expose raw SQL queries, internal server file paths, or raw Python stack traces to the HTTP frontend.
- Do not expose files in `storage/` directly via static web server routes.

## Rule 4: Mandatory Quality Gates
- No task is complete without running and passing:
  1. `pytest` (Complete unit & integration test suite)
  2. `python manage.py check` (Django system check)
  3. `python manage.py makemigrations --check` (Model & migration integrity check)

## Rule 5: Context Window Management
- Keep prompt context minimal and focused.
- Perform incremental, well-tested edits rather than large opportunistic refactorings.
