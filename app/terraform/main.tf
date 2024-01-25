# TODO: actually provision MongoDB
variable "mongodbatlas_public_key" {
  description = "MongoDB Atlas Public Key"
  type        = string
}

variable "mongodbatlas_private_key" {
  description = "MongoDB Atlas Private Key"
  type        = string
}

variable "aws_region" {
  description = "AWS Region"
  type        = string
}

variable "aws_access_key" {
  description = "AWS Access Key"
  type        = string
}

variable "aws_secret_access_key" {
  description = "AWS Secret Key"
  type        = string
}

provider "aws" {
  region = var.aws_region
  access_key = var.aws_access_key
  secret_key = var.aws_secret_access_key
}

resource "aws_s3_bucket" "ai_persona_app_bucket" {
  bucket = "ai-persona-app"
}

resource "aws_s3_bucket_policy" "ai_persona_app_bucket_policy" {
  bucket = aws_s3_bucket.ai_persona_app_bucket.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          AWS = ["arn:aws:iam::912531404540:user/ai-persona-app", ]
        }
        Action = "s3:*"
        Resource = [
          "${aws_s3_bucket.ai_persona_app_bucket.arn}",
          "${aws_s3_bucket.ai_persona_app_bucket.arn}/*"
        ]
      }
    ]
  })
}

resource "aws_ecr_repository" "ai_persona_app_ecr_repo" {
  name                 = "ai-persona-app"
  image_tag_mutability = "IMMUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }
}

# TODO: split the below into a different terraform file, must have ECR repo and have pushed image to it before trying to set up ECS
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
        },
      },
    ],
  })
}

resource "aws_iam_role_policy_attachment" "ecs_execution_role_policy" {
  role       = aws_iam_role.ecs_execution_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

resource "aws_iam_role_policy_attachment" "ecr_read_policy" {
  role       = aws_iam_role.ecs_execution_role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryReadOnly"
}

resource "aws_ecs_cluster" "ai_persona_app_cluster" {
  name = "ai-persona-app"
}

resource "aws_ecs_task_definition" "ai_persona_app_task" {
  family                   = "ai-persona-app-task-family"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = "256"
  memory                   = "512"
  execution_role_arn       = aws_iam_role.ecs_execution_role.arn

  container_definitions = jsonencode([{
    name  = "ai-persona-app-container",
    # TODO: figure out doing this dynamically, actual deployment should be done with GitHub Actions
    # so it shouldn't be a problem - need to make Actions remove latest tag and tag new image
    # with latest, otherwise running this terraform will revert the container image to whatever
    # latest tag it finds (could be multiple)
    image = "${aws_ecr_repository.ai_persona_app_ecr_repo.repository_url}:latest",
    portMappings = [{
      containerPort = 3000,
      hostPort      = 3000
    }]
  }])
}

resource "aws_vpc" "app_vpc" {
  cidr_block = "10.0.0.0/16"

  tags = {
    Name = "app-vpc"
  }
}

resource "aws_internet_gateway" "app_igw" {
  vpc_id = aws_vpc.app_vpc.id

  tags = {
    Name = "app-internet-gateway"
  }
}

resource "aws_route" "internet_access" {
  route_table_id         = aws_vpc.app_vpc.main_route_table_id
  destination_cidr_block = "0.0.0.0/0"
  gateway_id             = aws_internet_gateway.app_igw.id
}

resource "aws_subnet" "public_subnet_1" {
  vpc_id            = aws_vpc.app_vpc.id
  cidr_block        = "10.0.1.0/24"
  availability_zone = "us-east-1a"
  map_public_ip_on_launch = true

  tags = {
    Name = "public-subnet-1"
  }
}

resource "aws_subnet" "public_subnet_2" {
  vpc_id            = aws_vpc.app_vpc.id
  cidr_block        = "10.0.2.0/24"
  availability_zone = "us-east-1b"
  map_public_ip_on_launch = true

  tags = {
    Name = "public-subnet-2"
  }
}

resource "aws_security_group" "alb_security_group" {
  name        = "alb-security-group"
  description = "Security group for ALB"
  vpc_id      = aws_vpc.app_vpc.id

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_lb" "public_load_balancer" {
  name               = "public-load-balancer"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.alb_security_group.id]
  subnets            = [aws_subnet.public_subnet_1.id, aws_subnet.public_subnet_2.id]

  enable_deletion_protection = false

  tags = {
    Name = "public-load-balancer"
  }
}

resource "aws_lb_target_group" "target_group" {
  name     = "target-group"
  port     = 80
  protocol = "HTTP"
  vpc_id   = aws_vpc.app_vpc.id
  target_type = "ip"

  health_check {
    enabled             = true
    path                = "/api/health"  # Update this if your Next.js app has a specific health check path
    protocol            = "HTTP"
    healthy_threshold   = 2
    unhealthy_threshold = 2
    timeout             = 5
    interval            = 30
    matcher             = "200"
  }
}

resource "aws_lb_listener" "front_end_listener" {
  load_balancer_arn = aws_lb.public_load_balancer.arn
  port              = 80
  protocol          = "HTTP"

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.target_group.arn
  }
}

resource "aws_ecs_service" "ai_persona_app_service" {
  name            = "ai-persona-app-service"
  cluster         = aws_ecs_cluster.ai_persona_app_cluster.id
  task_definition = aws_ecs_task_definition.ai_persona_app_task.arn
  launch_type     = "FARGATE"

  network_configuration {
    subnets = [
      aws_subnet.public_subnet_1.id, 
      aws_subnet.public_subnet_2.id
    ]
    security_groups = [aws_security_group.alb_security_group.id]
  }

  desired_count = 1

  load_balancer {
    target_group_arn = aws_lb_target_group.target_group.arn
    container_name   = "ai-persona-app-container"
    container_port   = 3000
  }

  depends_on = [
    aws_lb_listener.front_end_listener
  ]

  # lifecycle {
  #   ignore_changes = [
  #     task_definition  # Ignoring changes to prevent Terraform from replacing the service on every new task definition revision.
  #   ]
  # }
}

# TODO: provisioning seems to mostly work, but actual service deployment is failing. Could
# be a network issue, misconfigured task definition/vpcs.etc


# TODO: invalid policy, is it needed?
# resource "aws_ecr_repository_policy" "ai_persona_app_ecr_policy" {
#   repository = aws_ecr_repository.ai_persona_app_ecr_repo.name

#   policy = jsonencode({
#     Version = "2012-10-17"
#     Statement = [
#       {
#         Effect = "Allow"
#         Principal = {
#           AWS = ["arn:aws:iam::912531404540:user/ai-persona-app"]
#         }
#         Action = [
#           "ecr:GetDownloadUrlForLayer",
#           "ecr:BatchGetImage",
#           "ecr:BatchCheckLayerAvailability",
#           "ecr:PutImage",
#           "ecr:InitiateLayerUpload",
#           "ecr:UploadLayerPart",
#           "ecr:CompleteLayerUpload"
#         ]
#         Resource = aws_ecr_repository.ai_persona_app_ecr_repo.arn
#       }
#     ]
#   })
# }
