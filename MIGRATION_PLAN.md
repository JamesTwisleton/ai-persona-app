# Migrate Production from AWS ECS to Fly.io

## Context
AWS bill has ballooned to >$100/month. The main costs are ECS Fargate (~$40), ALB (~$25), and RDS (~$20). Fly.io is already used for PR preview environments so the tooling and deploy patterns already exist. This migration should bring costs to ~$10-15/month.

**Decisions:**
- Keep S3 for avatar storage (cheap, no data migration needed)
- Keep custom domain (personacomposer.app)
- Archive Terraform files (don't delete)

---

## Step 1: Create production fly.toml files

Two new files based on the inline config already generated in `preview-env.yml` (lines 72-103 and 133-154), but adapted for production.

### `backend/fly.production.toml`
```toml
app = "persona-composer-be"
primary_region = "lhr"

[build]
dockerfile = "Dockerfile"

[processes]
app = "uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 1"

[http_service]
internal_port = 8000
force_https = true
auto_stop_machines = "suspend"
auto_start_machines = true
min_machines_running = 0
processes = ["app"]

[checks]
[checks.health]
type = "http"
port = 8000
path = "/health"
interval = "10s"
timeout = "5s"
grace_period = "30s"
processes = ["app"]

[[vm]]
size = "shared-cpu-1x"
memory = "512mb"
```

Key differences from preview:
- Fixed app name (`persona-composer-be` not `persona-pr-X-be`)
- `min_machines_running = 0` + `auto_stop = "suspend"` keeps costs low when idle
- 1 worker (matching preview, avoids OOM on 512MB — commit `773a0e3` already proved 1 worker needed)

### `frontend/fly.production.toml`
```toml
app = "persona-composer-fe"
primary_region = "lhr"

[build]
dockerfile = "Dockerfile"

[build.args]
NEXT_PUBLIC_API_URL = "https://api.personacomposer.app"

[http_service]
internal_port = 3000
force_https = true
auto_stop_machines = "suspend"
auto_start_machines = true
min_machines_running = 0

[[vm]]
size = "shared-cpu-1x"
memory = "256mb"
```

Key difference from preview: `NEXT_PUBLIC_API_URL` points to the production custom domain, not a `.fly.dev` URL. No `NEXT_PUBLIC_PREVIEW_MODE`.

---

## Step 2: Add new Fly.io deploy workflows (keep ECS workflows unchanged)

Instead of modifying the existing CI workflows, we add **new** Fly.io deploy workflows alongside them. A GitHub Actions repository variable `DEPLOY_TARGET` controls which platform deploys run on. This means rollback is a single variable change — no code revert needed.

### How the toggle works

- Set GitHub repo variable `DEPLOY_TARGET` to `"fly"` to deploy to Fly.io
- Set it to `"ecs"` (or remove it) to deploy to AWS ECS
- Change takes effect on the next push to main — no code changes required

### Existing workflows — add deploy target guard

Add a condition to the existing `backend-deploy` and `frontend-deploy` jobs so they only run when `DEPLOY_TARGET != 'fly'`.

**`.github/workflows/python-ci.yml`** — change the `backend-deploy` job's `if`:
```yaml
  backend-deploy:
    name: Backend deploy
    runs-on: ubuntu-latest
    needs: backend-tests
    if: github.ref == 'refs/heads/main' && github.event_name == 'push' && vars.DEPLOY_TARGET != 'fly'
```

**`.github/workflows/nextjs-ci.yml`** — change the `frontend-deploy` job's `if`:
```yaml
  frontend-deploy:
    name: Frontend deploy
    runs-on: ubuntu-latest
    needs: frontend-tests
    if: github.ref == 'refs/heads/main' && github.event_name == 'push' && vars.DEPLOY_TARGET != 'fly'
```

This is the **only** change to existing workflows — everything else stays intact.

### New workflow: `.github/workflows/fly-production.yml`

A single new workflow that deploys both backend and frontend to Fly.io, only when `DEPLOY_TARGET == 'fly'`. It reuses the existing test jobs by depending on the CI workflows via `workflow_run`.

```yaml
name: Production Deploy (Fly.io)

on:
  push:
    branches: [main]

jobs:
  backend-deploy:
    name: Backend deploy (Fly.io)
    runs-on: ubuntu-latest
    if: vars.DEPLOY_TARGET == 'fly'

    steps:
      - uses: actions/checkout@v4

      - name: Install flyctl
        uses: superfly/flyctl-actions/setup-flyctl@master

      - name: Set backend secrets
        env:
          FLY_API_TOKEN: ${{ secrets.FLY_API_TOKEN }}
        run: |
          flyctl secrets set \
            --app persona-composer-be \
            JWT_SECRET="${{ secrets.JWT_SECRET }}" \
            ANTHROPIC_API_KEY="${{ secrets.ANTHROPIC_API_KEY }}" \
            OPENAI_API_KEY="${{ secrets.OPENAI_API_KEY }}" \
            GOOGLE_CLIENT_ID="${{ secrets.GOOGLE_CLIENT_ID }}" \
            GOOGLE_CLIENT_SECRET="${{ secrets.GOOGLE_CLIENT_SECRET }}" \
            FRONTEND_URL="https://personacomposer.app" \
            GOOGLE_REDIRECT_URI="https://api.personacomposer.app/auth/callback/google" \
            S3_AVATAR_BUCKET="persona-composer-avatars" \
            AWS_DEFAULT_REGION="eu-west-1" \
            AWS_ACCESS_KEY_ID="${{ secrets.AWS_ACCESS_KEY_ID }}" \
            AWS_SECRET_ACCESS_KEY="${{ secrets.AWS_SECRET_ACCESS_KEY }}" \
            ENV="production" \
            LOG_LEVEL="INFO" \
            --stage

      - name: Deploy backend
        working-directory: backend
        env:
          FLY_API_TOKEN: ${{ secrets.FLY_API_TOKEN }}
        run: |
          flyctl deploy \
            --config fly.production.toml \
            --build-target production \
            --wait-timeout 300

      - name: Smoke test
        run: |
          sleep 10
          curl --fail --silent --show-error \
            --retry 5 --retry-delay 5 --retry-connrefused \
            https://api.personacomposer.app/health

  frontend-deploy:
    name: Frontend deploy (Fly.io)
    runs-on: ubuntu-latest
    if: vars.DEPLOY_TARGET == 'fly'

    steps:
      - uses: actions/checkout@v4

      - name: Install flyctl
        uses: superfly/flyctl-actions/setup-flyctl@master

      - name: Deploy frontend
        working-directory: frontend
        env:
          FLY_API_TOKEN: ${{ secrets.FLY_API_TOKEN }}
        run: |
          flyctl deploy \
            --config fly.production.toml \
            --build-target production \
            --wait-timeout 300

      - name: Smoke test
        run: |
          sleep 10
          curl --fail --silent --show-error \
            --retry 5 --retry-delay 5 --retry-connrefused \
            https://personacomposer.app
```

**Notes:**
- S3 still works: AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY are passed as Fly secrets so boto3 can access S3
- DATABASE_URL is NOT set here — Fly Postgres attach sets it automatically
- `NEXT_PUBLIC_API_URL` is in `fly.production.toml` as a build arg
- Both jobs run in parallel (backend and frontend are independent)

### Manual ECS deploy workflows — unchanged

The manual-trigger workflows (`python-docker-ecr-ecs.yml` and `nextjs-docker-ecr-ecs.yml`) stay as-is. They're `workflow_dispatch` only, so they won't fire automatically. They serve as an emergency fallback — you can manually trigger an ECS redeploy at any time.

---

## Step 3: Rollback procedure

If Fly.io isn't working, rollback is:

### Quick rollback (DNS only, ~5 min)
If the ECS services are still running:
1. Point DNS back to the ALB (revert Route53 A records)
2. App is back on AWS within DNS propagation time

### Full rollback (~15 min)
If you've already switched `DEPLOY_TARGET`:
1. Go to GitHub repo **Settings > Secrets and variables > Actions > Variables**
2. Change `DEPLOY_TARGET` from `fly` to `ecs` (or delete it)
3. Point DNS back to the ALB
4. Push any commit to main (or manually trigger the ECS deploy workflows)
5. ECS redeploys from the latest ECR image

### Why this works
- ECS infrastructure stays up until you explicitly `terraform destroy` (Step 7)
- ECR still has your latest images (lifecycle policy keeps last 5)
- RDS still has your data
- AWS Secrets Manager still has all secrets
- The only thing that changed is which deploy job runs on push to main
- Manual ECS deploy workflows are always available as a safety net

---

## Step 4: Add Fly.io domains to frontend Next.js image config

**File:** `frontend/next.config.mjs`

Add Fly.io app domains so Next.js Image component can load images served from Fly (if any). The S3 patterns already handle avatar presigned URLs, but add Fly domains for completeness:

```js
{
  protocol: "https",
  hostname: "*.fly.dev",
},
```

This covers both preview (`persona-pr-X-be.fly.dev`) and production (if ever accessed via `.fly.dev` directly).

---

## Step 5: Archive Terraform directory

**New file:** `terraform/ARCHIVED.md`

```markdown
# Archived — AWS Infrastructure

These Terraform files defined the original AWS infrastructure (ECS, ALB, RDS, etc.).
Production was migrated to Fly.io in April 2026 to reduce costs.

Kept for reference. Do not apply.

To fully decommission AWS resources, run `terraform destroy` from this directory.
```

No changes to any `.tf` files.

---

## Step 6: Manual steps (before first deploy)

These are one-time setup commands to run locally before merging the code changes.

### 6a. Create production Fly apps
```bash
flyctl apps create persona-composer-be --org personal
flyctl apps create persona-composer-fe --org personal
```

### 6b. Create Fly Postgres and attach to backend
```bash
flyctl postgres create \
  --name persona-composer-db \
  --org personal \
  --region lhr \
  --vm-size shared-cpu-1x \
  --initial-cluster-size 1 \
  --volume-size 1

flyctl postgres attach persona-composer-db --app persona-composer-be
```

This auto-sets `DATABASE_URL` on the backend app.

### 6c. Migrate data from RDS (optional)
If you want to preserve existing users/personas/conversations:
```bash
# Dump from RDS
pg_dump -h <rds-endpoint> -U <user> -d <dbname> --no-owner --no-acl > dump.sql

# Restore (proxy Fly Postgres locally first)
flyctl proxy 15432:5432 --app persona-composer-db
psql -h localhost -p 15432 -U <fly-user> -d <fly-db> < dump.sql
```

### 6d. Set initial secrets on backend app
```bash
flyctl secrets set \
  --app persona-composer-be \
  JWT_SECRET="<your-jwt-secret>" \
  ANTHROPIC_API_KEY="<key>" \
  OPENAI_API_KEY="<key>" \
  GOOGLE_CLIENT_ID="<id>" \
  GOOGLE_CLIENT_SECRET="<secret>" \
  FRONTEND_URL="https://personacomposer.app" \
  GOOGLE_REDIRECT_URI="https://api.personacomposer.app/auth/callback/google" \
  S3_AVATAR_BUCKET="persona-composer-avatars" \
  AWS_DEFAULT_REGION="eu-west-1" \
  AWS_ACCESS_KEY_ID="<key>" \
  AWS_SECRET_ACCESS_KEY="<secret>" \
  ENV="production" \
  LOG_LEVEL="INFO"
```

### 6e. Add GitHub repo secrets
```bash
# Create a Fly deploy token
flyctl tokens create deploy --expiry 8760h
```

Add/verify these GitHub repo secrets:
- `FLY_API_TOKEN` — the deploy token from above
- `JWT_SECRET` — (was in AWS Secrets Manager, needs adding to GitHub)
- `GOOGLE_CLIENT_ID` — (was in AWS Secrets Manager, needs adding to GitHub)
- `GOOGLE_CLIENT_SECRET` — (was in AWS Secrets Manager, needs adding to GitHub)
- `ANTHROPIC_API_KEY` — (already exists)
- `OPENAI_API_KEY` — (already exists)
- `AWS_ACCESS_KEY_ID` — (already exists, still needed for S3)
- `AWS_SECRET_ACCESS_KEY` — (already exists, still needed for S3)

### 6f. Configure custom domains on Fly.io
```bash
# Frontend — personacomposer.app
flyctl certs add personacomposer.app --app persona-composer-fe

# Backend — api.personacomposer.app
flyctl certs add api.personacomposer.app --app persona-composer-be
```

Fly will output the required DNS records (CNAME or A/AAAA). Update your DNS:
- If keeping Route53: update the A records to point to Fly's IPs instead of the ALB
- If moving DNS: point your domain registrar's nameservers elsewhere

### 6g. Update Google OAuth redirect URI
In Google Cloud Console, verify the authorized redirect URI is set to:
- `https://api.personacomposer.app/auth/callback/google`

(This stays the same since we're keeping the domain, but worth verifying.)

---

## Step 7: Tear down AWS (after verifying Fly.io works)

Only do this after the app is confirmed working on Fly.io:

```bash
cd terraform

# Preview what will be destroyed
terraform plan -destroy

# Destroy everything EXCEPT the S3 bucket
terraform destroy
```

**Keep alive on AWS:**
- S3 bucket (`persona-composer-avatars`) — still used for avatars
- IAM user/credentials for S3 access — still needed by backend on Fly
- Route53 hosted zone — if you're still using Route53 for DNS
- Terraform state bucket — can delete after final destroy

**Safe to destroy:**
- ECS cluster, services, task definitions
- ALB, target groups, listeners
- RDS instance
- ECR repositories
- VPC, subnets, security groups, internet gateway
- ACM certificate (Fly handles SSL)
- CloudWatch log groups
- Secrets Manager secrets (now in Fly secrets)

---

## Summary of changes

### Files to create
| File | Purpose |
|------|---------|
| `backend/fly.production.toml` | Production Fly config for backend |
| `frontend/fly.production.toml` | Production Fly config for frontend |
| `.github/workflows/fly-production.yml` | Fly.io deploy workflow (runs when `DEPLOY_TARGET=fly`) |
| `terraform/ARCHIVED.md` | Note that Terraform is no longer active |

### Files to modify
| File | Change |
|------|--------|
| `.github/workflows/python-ci.yml` | Add `vars.DEPLOY_TARGET != 'fly'` guard to `backend-deploy` job |
| `.github/workflows/nextjs-ci.yml` | Add `vars.DEPLOY_TARGET != 'fly'` guard to `frontend-deploy` job |
| `frontend/next.config.mjs` | Add `*.fly.dev` to image remote patterns |

### Files unchanged (kept for rollback)
| File | Reason |
|------|--------|
| `.github/workflows/python-docker-ecr-ecs.yml` | Manual ECS deploy — emergency rollback |
| `.github/workflows/nextjs-docker-ecr-ecs.yml` | Manual ECS deploy — emergency rollback |
| `terraform/*.tf` | All Terraform files intact for `terraform destroy` or rollback |

---

## Verification checklist

### Phase 1: Deploy to Fly.io (AWS still running)
1. **Pre-merge (manual):** Complete steps 6a-6f above
2. **Set variable:** Add `DEPLOY_TARGET=fly` in GitHub repo Settings > Variables
3. **Merge to main:** Watch GitHub Actions — Fly.io deploy should run, ECS deploy should skip
4. **Test via .fly.dev URLs first** (before switching DNS):
   - `curl https://persona-composer-be.fly.dev/health` returns 200
   - `https://persona-composer-fe.fly.dev` loads the app
5. **Switch DNS:** Point `personacomposer.app` and `api.personacomposer.app` to Fly.io
6. **Wait for DNS propagation** (~5-30 min), then verify on custom domain:
   - `curl https://api.personacomposer.app/health` returns 200
   - `https://personacomposer.app` loads the app
   - Google OAuth login/logout works
   - Avatar generation works (S3 upload + presigned URL display)
   - Existing data is present (users, personas, conversations)

### Phase 2: Soak period (keep AWS running as fallback)
7. **Run both platforms for 1-2 weeks.** AWS costs continue but you have instant rollback.
8. **Monitor:** Check Fly.io dashboard for errors, cold start times, memory usage
9. **Auto-stop:** After ~5 min idle, machines should suspend. Next request wakes them (~2-5s)

### Phase 3: Tear down AWS (only after confidence)
10. **Tear down:** Run `terraform destroy` per Step 7 (keep S3 bucket + IAM for S3)
11. **Clean up:** Remove `DEPLOY_TARGET` variable, remove ECS guard conditions from CI workflows (optional)
