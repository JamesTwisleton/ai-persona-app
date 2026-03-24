#!/usr/bin/env bash
# deploy.sh — Build, push, and deploy Persona Composer to AWS
#
# Usage:
#   ./deploy.sh          # Full deploy (infra + images + force redeploy)
#   ./deploy.sh infra    # Terraform only
#   ./deploy.sh images   # Build + push Docker images only
#   ./deploy.sh redeploy # Force ECS services to pull latest images

set -euo pipefail

REGION="us-east-1"
APP_NAME="persona-composer"
FRONTEND_API_URL="https://api.personacomposer.app"
BOLD='\033[1m'
GREEN='\033[0;32m'
CYAN='\033[0;36m'
RESET='\033[0m'

step() { echo -e "\n${BOLD}=== $1 ===${RESET}"; }
ok()   { echo -e "${GREEN}✓ $1${RESET}"; }

# ============================================================
# 1. Terraform — provision / update infrastructure
# ============================================================

infra() {
  step "Provisioning infrastructure with Terraform"

  cd "$(dirname "$0")/terraform"

  terraform init -upgrade
  terraform plan -out=tfplan
  terraform apply tfplan

  # Capture ECR URLs from Terraform outputs
  ECR_BACKEND=$(terraform output -raw ecr_backend_url)
  ECR_FRONTEND=$(terraform output -raw ecr_frontend_url)
  CLUSTER=$(terraform output -raw ecs_cluster_name)

  cd ..

  ok "Infrastructure ready"
  echo "  Backend ECR:  $ECR_BACKEND"
  echo "  Frontend ECR: $ECR_FRONTEND"
}

# ============================================================
# 2. Build & push Docker images to ECR
# ============================================================

images() {
  step "Building and pushing Docker images"

  cd "$(dirname "$0")/terraform"
  ECR_BACKEND=$(terraform output -raw ecr_backend_url)
  ECR_FRONTEND=$(terraform output -raw ecr_frontend_url)
  cd ..

  ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
  ECR_REGISTRY="${ACCOUNT_ID}.dkr.ecr.${REGION}.amazonaws.com"

  # Authenticate Docker with ECR
  echo "Authenticating with ECR..."
  aws ecr get-login-password --region "$REGION" \
    | docker login --username AWS --password-stdin "$ECR_REGISTRY"

  # --- Backend ---
  echo -e "\n${CYAN}Building backend...${RESET}"
  docker build \
    --platform linux/amd64 \
    --target production \
    -t "${ECR_BACKEND}:latest" \
    ./backend

  echo "Pushing backend..."
  docker push "${ECR_BACKEND}:latest"
  ok "Backend pushed"

  # --- Frontend ---
  echo -e "\n${CYAN}Building frontend...${RESET}"
  docker build \
    --platform linux/amd64 \
    --target production \
    --build-arg NEXT_PUBLIC_API_URL="$FRONTEND_API_URL" \
    -t "${ECR_FRONTEND}:latest" \
    ./frontend

  echo "Pushing frontend..."
  docker push "${ECR_FRONTEND}:latest"
  ok "Frontend pushed"
}

# ============================================================
# 3. Force ECS services to redeploy with latest images
# ============================================================

redeploy() {
  step "Forcing ECS redeployment"

  cd "$(dirname "$0")/terraform"
  CLUSTER=$(terraform output -raw ecs_cluster_name)
  cd ..

  aws ecs update-service \
    --region "$REGION" \
    --cluster "$CLUSTER" \
    --service "${APP_NAME}-backend" \
    --force-new-deployment \
    --output text --query 'service.serviceName'

  aws ecs update-service \
    --region "$REGION" \
    --cluster "$CLUSTER" \
    --service "${APP_NAME}-frontend" \
    --force-new-deployment \
    --output text --query 'service.serviceName'

  ok "ECS services redeploying"
  echo ""
  echo "  Monitor at: https://us-east-1.console.aws.amazon.com/ecs/v2/clusters/${CLUSTER}/services"
  echo "  Live site:  https://personacomposer.app"
}

# ============================================================
# Entry point
# ============================================================

MODE="${1:-all}"

case "$MODE" in
  infra)    infra ;;
  images)   images ;;
  redeploy) redeploy ;;
  all)
    infra
    images
    redeploy
    step "Deploy complete"
    echo -e "  ${GREEN}https://personacomposer.app${RESET}"
    ;;
  *)
    echo "Usage: ./deploy.sh [all|infra|images|redeploy]"
    exit 1
    ;;
esac
