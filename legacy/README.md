# Legacy Code Archive

This directory contains the previous implementation of the AI Focus Groups application.

## What's Here

The `code/` directory contains the original prototype built with:
- **Frontend**: Next.js (still relevant, may be migrated)
- **Backend**: Flask/Dash (being replaced with FastAPI)
- **Infrastructure**: Terraform (will be updated)

## Why It Was Moved

Per the project specification (CLAUDE.md):
> "The application must be rebuilt from scratch using an idiomatic, modern stack."

The new implementation follows:
- **Test-Driven Development (TDD)** - all tests written before code
- **Modern 2026 Standards** - FastAPI instead of Flask
- **Comprehensive Testing** - 90%+ coverage requirement
- **Clean Architecture** - Proper separation of concerns

## Reference Material

This code can be referenced for:
- Understanding the original personality vector algorithm (`utils.py`, `personas.json`)
- UI/UX patterns from the Next.js frontend
- Database schema concepts
- Terraform infrastructure patterns

## DO NOT USE FOR PRODUCTION

This code is archived for reference only. All new development should occur in:
- `/backend` - FastAPI backend
- `/frontend` - Next.js frontend (new clean setup)
- `/infrastructure` - Updated Terraform configs

---

**Date Archived**: 2026-01-31
**Reason**: Rebuild from scratch with TDD and modern stack
