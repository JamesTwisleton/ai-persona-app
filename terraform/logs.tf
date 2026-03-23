resource "aws_cloudwatch_log_group" "backend" {
  name              = "/ecs/${var.app_name}/backend"
  retention_in_days = 30
  tags              = { Name = "${var.app_name}-backend-logs" }
}

resource "aws_cloudwatch_log_group" "frontend" {
  name              = "/ecs/${var.app_name}/frontend"
  retention_in_days = 30
  tags              = { Name = "${var.app_name}-frontend-logs" }
}
