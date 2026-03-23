data "aws_iam_policy_document" "ecs_assume_role" {
  statement {
    actions = ["sts:AssumeRole"]
    principals {
      type        = "Service"
      identifiers = ["ecs-tasks.amazonaws.com"]
    }
  }
}

# ============================================================
# ECS Execution Role — used by ECS to pull images and write logs
# ============================================================

resource "aws_iam_role" "ecs_execution" {
  name               = "${var.app_name}-ecs-execution-role"
  assume_role_policy = data.aws_iam_policy_document.ecs_assume_role.json
}

resource "aws_iam_role_policy_attachment" "ecs_execution_managed" {
  role       = aws_iam_role.ecs_execution.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

# Allow execution role to read Secrets Manager secrets
resource "aws_iam_role_policy" "ecs_execution_secrets" {
  name = "${var.app_name}-ecs-secrets-policy"
  role = aws_iam_role.ecs_execution.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "secretsmanager:GetSecretValue"
        ]
        Resource = [
          aws_secretsmanager_secret.anthropic_api_key.arn,
          aws_secretsmanager_secret.openai_api_key.arn,
          aws_secretsmanager_secret.jwt_secret.arn,
          aws_secretsmanager_secret.google_client_id.arn,
          aws_secretsmanager_secret.google_client_secret.arn,
          aws_secretsmanager_secret.db_url.arn,
        ]
      }
    ]
  })
}

# ============================================================
# ECS Task Role — permissions for the running application
# Currently the app only calls external APIs so this is minimal
# ============================================================

resource "aws_iam_role" "ecs_task" {
  name               = "${var.app_name}-ecs-task-role"
  assume_role_policy = data.aws_iam_policy_document.ecs_assume_role.json
}
