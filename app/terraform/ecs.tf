# VPC Definition
resource "aws_vpc" "ai_persona_app_vpc" {
  cidr_block = "10.0.0.0/16"
  enable_dns_support   = true
  enable_dns_hostnames = true

  tags = {
    Name = "ai-persona-app-vpc"
  }
}

# Subnet Definitions
resource "aws_subnet" "ai_persona_app_subnet_0" {
  vpc_id            = aws_vpc.ai_persona_app_vpc.id
  cidr_block        = "10.0.1.0/24"
  availability_zone = "us-east-1a"
}

resource "aws_subnet" "ai_persona_app_subnet_1" {
  vpc_id            = aws_vpc.ai_persona_app_vpc.id
  cidr_block        = "10.0.2.0/24"
  availability_zone = "us-east-1b"
}

# Security Group Definition to allow internet access
resource "aws_security_group" "allow_internet" {
  name        = "allow_internet"
  description = "Allow internet access"
  vpc_id      = aws_vpc.ai_persona_app_vpc.id

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# Provision IAM Role for ECS Task Execution
resource "aws_iam_role" "ecs_execution_role" {
  name = "ecs_execution_role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Action = "sts:AssumeRole",
        Effect = "Allow",
        Principal = {
          Service = "ecs-tasks.amazonaws.com"
        }
      }
    ]
  })
}

# Attach the AmazonECSTaskExecutionRolePolicy to the role
resource "aws_iam_role_policy_attachment" "ecs_task_execution_role_policy" {
  role       = aws_iam_role.ecs_execution_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

# Provision ECS Cluster
resource "aws_ecs_cluster" "ai_persona_app_cluster" {
  name = "ai-persona-app-cluster"
}

# ECS Task Definition that references the ECR repository
resource "aws_ecs_task_definition" "ai_persona_app_task" {
  family                   = "ai-persona-app-task"
  network_mode             = "awsvpc"
  execution_role_arn       = aws_iam_role.ecs_execution_role.arn
  requires_compatibilities = ["FARGATE"]
  cpu                      = "256" # CPU units
  memory                   = "512" # Memory in MiB

  container_definitions = jsonencode([
    {
      name  = "my-container",
      image = "${aws_ecr_repository.ai_persona_app_ecr_repo.repository_url}:latest",
      portMappings = [
        {
          containerPort = 3000,
          hostPort      = 3000,
        },
      ],
    },
  ])
}

# ECS Service that runs on Fargate and uses subnets, security group and the task definition
resource "aws_ecs_service" "ai_persona_app_ecs_service" {
  name            = "ai-persona-app-service"
  cluster         = aws_ecs_cluster.ai_persona_app_cluster.id
  task_definition = aws_ecs_task_definition.ai_persona_app_task.arn
  launch_type     = "FARGATE"
  network_configuration {
    subnets         = [aws_subnet.ai_persona_app_subnet_0.id, aws_subnet.ai_persona_app_subnet_1.id]
    security_groups = [aws_security_group.allow_internet.id]
  }
  desired_count = 1 # Number of tasks to run
}

output "service_url" {
  value = aws_ecs_service.ai_persona_app_ecs_service.name
}
