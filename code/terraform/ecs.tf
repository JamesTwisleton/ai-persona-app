# Define a Virtual Private Cloud (VPC) for the network environment.
# This provides a logically isolated section of the AWS Cloud to launch resources.
resource "aws_vpc" "ai_persona_app_vpc" {
  cidr_block = "10.0.0.0/16"           # The IP address range for the VPC
  enable_dns_support   = true          # Enable DNS support within the VPC
  enable_dns_hostnames = true          # Enable DNS hostnames within the VPC

  tags = {
    Name = "ai-persona-app-vpc"        # Name tag for identifying the VPC
  }
}

# Create an Internet Gateway.
# An Internet Gateway enables communication between your VPC and the internet.
resource "aws_internet_gateway" "ai_persona_app_igw" {
  vpc_id = aws_vpc.ai_persona_app_vpc.id  # Associate the Internet Gateway with your VPC

  tags = {
    Name = "ai-persona-app-igw"  # Name tag for identifying the Internet Gateway
  }
}

# Create a route in the main route table for the VPC.
# This route will direct traffic from the VPC to the Internet Gateway, enabling internet access.
resource "aws_route" "ai_persona_app_route" {
  route_table_id         = aws_vpc.ai_persona_app_vpc.main_route_table_id  # The main route table associated with the VPC
  destination_cidr_block = "0.0.0.0/0"                                     # Represents all IP addresses (i.e., internet traffic)
  gateway_id             = aws_internet_gateway.ai_persona_app_igw.id      # The ID of the Internet Gateway
}

# Define two subnets within the VPC.
# Subnets allow partitioning the network inside the VPC.
resource "aws_subnet" "ai_persona_app_subnet0" {
  vpc_id            = aws_vpc.ai_persona_app_vpc.id  # Associate with the created VPC
  cidr_block        = "10.0.1.0/24"                  # The IP address range for the subnet
  availability_zone = "us-east-1a"                   # Availability Zone for the subnet

  tags = {
    Name = "ai-persona-app-subnet0"                  # Name tag for the subnet
  }
}

resource "aws_subnet" "ai_persona_app_subnet1" {
  vpc_id            = aws_vpc.ai_persona_app_vpc.id  # Associate with the created VPC
  cidr_block        = "10.0.2.0/24"                  # The IP address range for the subnet
  availability_zone = "us-east-1b"                   # Availability Zone for the subnet

  tags = {
    Name = "ai-persona-app-subnet1"                  # Name tag for the subnet
  }
}

resource "aws_acm_certificate" "ai_persona_app_certificate" {
  domain_name       = "personacomposer.app"
  validation_method = "DNS"
}

resource "aws_route53_zone" "ai_persona_app_hosted_zone" {
  name = "personacomposer.app"
}

# Define a security group for the VPC.
# Security groups act as a virtual firewall to control inbound and outbound traffic.
resource "aws_security_group" "ai_persona_app_sg" {
  name        = "ai-persona-app-sg"
  description = "Allow inbound traffic"
  vpc_id      = aws_vpc.ai_persona_app_vpc.id        # Associate with the created VPC

  # Ingress rule: Allow inbound traffic from 0 to port 3000 (for the Next.js application).
  # TODO: figure out why simply doing port 80 doesn't work?
  ingress {
    from_port   = 0
    to_port     = 3000
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]                      # Allow traffic from any IP
  }

  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # Egress rule: Allow all outbound traffic.
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"                               # -1 means all protocols
    cidr_blocks = ["0.0.0.0/0"]                      # Allow to any IP
  }

  tags = {
    Name = "ai-persona-app-sg"                       # Name tag for the security group
  }
}

# Define an IAM role for ECS execution.
# This role is used by the ECS service itself to perform operations such as pulling Docker images 
# from Amazon Elastic Container Registry (ECR) and publishing log streams to Amazon CloudWatch. 
# This is distinct from the ECS task role, 
# which grants permissions to the application running within the ECS tasks.
resource "aws_iam_role" "ai_persona_app_ecs_execution_role" {
  name = "ai-persona-app-ecs-execution-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Action = "sts:AssumeRole",
        Effect = "Allow",
        Principal = {
          Service = "ecs-tasks.amazonaws.com"
        },
      },
    ],
  })

  inline_policy {
    name = "ECRAccessPolicy"
    policy = jsonencode({
      Version = "2012-10-17",
      Statement = [
        {
          Action = [
            "ecr:GetAuthorizationToken",
            "ecr:BatchCheckLayerAvailability",
            "ecr:GetDownloadUrlForLayer",
            "ecr:BatchGetImage",
            "logs:CreateLogStream",
            "logs:PutLogEvents"
          ],
          Effect = "Allow",
          Resource = "*"
        }
      ]
    })
  }
}

# Define an IAM role for ECS tasks.
# This role is attached to the ECS tasks themselves and provides permissions
# for the tasks to interact with specific AWS services that the application might need.
# This is different from the ECS execution role, which is used by the ECS service
# to pull images and publish logs.
resource "aws_iam_role" "ai_persona_app_ecs_task_role" {
  name = "ai-persona-app-ecs-task-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Action = "sts:AssumeRole",
        Effect = "Allow",
        Principal = {
          Service = "ecs-tasks.amazonaws.com"
        },
      },
    ],
  })

  inline_policy {
    name = "ai-persona-app-ecs-task-policy"
    policy = jsonencode({
      Version = "2012-10-17",
      Statement = [
        {
          Action = [
            "ecr:GetAuthorizationToken",
            "ecr:BatchCheckLayerAvailability",
            "ecr:GetDownloadUrlForLayer",
            "ecr:BatchGetImage",
            "logs:CreateLogStream",
            "logs:PutLogEvents"
          ],
          Effect = "Allow",
          Resource = "*"
        },
      ]
    })
  }
}

# Define the Amazon Elastic Container Service (ECS) task definition.
# This specifies the container configuration for the application.
resource "aws_ecs_task_definition" "ai_persona_app_task" {
  family                   = "ai-persona-app-task"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]            # Use Fargate for serverless container management
  cpu                      = "256"                  # CPU units for the task
  memory                   = "512"                  # Memory for the task
  execution_role_arn       = aws_iam_role.ai_persona_app_ecs_execution_role.arn
  task_role_arn            = aws_iam_role.ai_persona_app_ecs_task_role.arn

  # Container definition: Specifies the docker container configuration
  container_definitions = jsonencode([
    {
      name  = "ai-persona-app",
      image = "${aws_ecr_repository.ai_persona_app_ecr_repo.repository_url}:latest",
      portMappings = [
        {
          containerPort = 3000,
          hostPort      = 3000
        }
      ],
      logConfiguration = {
        logDriver = "awslogs",
        options = {
          awslogs-group         = aws_cloudwatch_log_group.ai_persona_app_log_group.name,
          awslogs-region        = "us-east-1",          # Replace with your AWS region
          awslogs-stream-prefix = "ecs"
        }
      },
      # TODO: put these in secret manager
      environment = [
        {
          name = "OPENAI_API_KEY",
          value = var.openai_api_key
        },
        {
          name = "REPLICATE_API_TOKEN",
          value = var.replicate_api_token
        },
        {
          name = "MONGODB_URI",
          value = var.mongodb_uri
        },
        {
          name = "MONGODB_DB",
          value = var.mongodb_db
        },
        {
          name = "AWS_ACCESS_KEY_ID",
          value = var.aws_access_key
        },
        {
          name = "AWS_SECRET_ACCESS_KEY",
          value = var.aws_secret_access_key
        },
        {
          name = "S3_BUCKET_NAME",
          value = aws_s3_bucket.ai_persona_app_bucket.bucket
        },
        {
          name = "BLUESKY_USERNAME",
          value = var.bluesky_username
        },
        {
          name = "BLUESKY_PASSWORD",
          value = var.bluesky_password
        },
        {
          name = "BLUESKY_PROFILE_BASE_URL",
          value = var.bluesky_profile_base_url
        }
      ]
    }
  ])
}

# Define an Application Load Balancer (ALB).
# The ALB will distribute incoming application traffic across multiple targets.
resource "aws_lb" "ai_persona_app_alb" {
  name               = "ai-persona-app-alb"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.ai_persona_app_sg.id]
  subnets            = [aws_subnet.ai_persona_app_subnet0.id, aws_subnet.ai_persona_app_subnet1.id]

  enable_deletion_protection = false

  tags = {
    Name = "ai-persona-app-alb"                    # Name tag for the ALB
  }
}

# Define a target group for the ALB.
# Target groups route requests to one or more registered targets.
resource "aws_lb_target_group" "ai_persona_app_tg" {
  name        = "ai-persona-app-tg"
  port        = 80
  protocol    = "HTTP"
  vpc_id      = aws_vpc.ai_persona_app_vpc.id
  target_type = "ip"

  # Health check settings for the target group
  health_check {
    healthy_threshold   = 2
    unhealthy_threshold = 2
    timeout             = 3
    interval            = 30
    matcher             = "200-299"
    path                = "/api/health"
  }

  depends_on = [
    aws_lb.ai_persona_app_alb
  ]
}

# HTTPS Listener for the ALB
resource "aws_lb_listener" "ai_persona_app_alb_https_listener" {
  load_balancer_arn = aws_lb.ai_persona_app_alb.arn
  port              = 443
  protocol          = "HTTPS"
  ssl_policy        = "ELBSecurityPolicy-2016-08"
  certificate_arn   = aws_acm_certificate.ai_persona_app_certificate.arn

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.ai_persona_app_tg.arn
  }
}

# HTTP to HTTPS Redirect
resource "aws_lb_listener" "ai_persona_app_alb_http_listener" {
  load_balancer_arn = aws_lb.ai_persona_app_alb.arn
  port              = 80
  protocol          = "HTTP"

  default_action {
    type = "redirect"

    redirect {
      port        = "443"
      protocol    = "HTTPS"
      status_code = "HTTP_301"
    }
  }
}

# Amazon CloudWatch log group so we can see the logs of the application
resource "aws_cloudwatch_log_group" "ai_persona_app_log_group" {
  name = "/ecs/ai-persona-app"                         # Name for the log group

  retention_in_days = 30                                # Log retention period in days

  tags = {
    Name = "ai-persona-app-log-group"
  }
}

# Define an Amazon Elastic Container Service (ECS) service.
# This service maintains the desired count of tasks and restarts tasks if they fail.
resource "aws_ecs_service" "ai_persona_app_service" {
  name            = "ai-persona-app-service"
  cluster         = aws_ecs_cluster.ai_persona_app_cluster.id
  task_definition = "${aws_ecs_task_definition.ai_persona_app_task.family}:${aws_ecs_task_definition.ai_persona_app_task.revision}"
  launch_type     = "FARGATE"

  # Network configuration for the service
  network_configuration {
    subnets = [aws_subnet.ai_persona_app_subnet0.id, aws_subnet.ai_persona_app_subnet1.id]
    security_groups = [aws_security_group.ai_persona_app_sg.id]
    assign_public_ip = true
  }

  # Load balancer configuration
  load_balancer {
    target_group_arn = aws_lb_target_group.ai_persona_app_tg.arn
    container_name   = "ai-persona-app"
    container_port   = 3000
  }

  desired_count = 1
  depends_on = [
    aws_lb_listener.ai_persona_app_alb_https_listener,
    aws_lb_listener.ai_persona_app_alb_http_listener,
    aws_ecs_task_definition.ai_persona_app_task
  ]
}


# Define an Amazon Elastic Container Service (ECS) cluster.
# A cluster is a grouping of tasks or services.
resource "aws_ecs_cluster" "ai_persona_app_cluster" {
  name = "ai-persona-app-cluster"                       # Name for the ECS cluster
}

# Output the DNS name of the ALB.
# This DNS name is used to access your service over the internet.
output "ai_persona_app_alb_dns_name" {
  value = aws_lb.ai_persona_app_alb.dns_name
  description = "The DNS name of the application load balancer"
}
