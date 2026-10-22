# --- AWS Provider Configuration ---
provider "aws" {
  region = "us-east-1"
}

# --- CI/CD Server Instance ---
resource "aws_instance" "cicd_server" {
  ami           = "ami-04a81a99f5ec58529" # Ubuntu 22.04 LTS (us-east-1)
  instance_type = "t3.medium"
  key_name      = "usnvi"         # Replace with your actual AWS key pair name

  vpc_security_group_ids = [aws_security_group.cicd_sg.id]

  tags = {
    Name = "ImageCompressor-CICD-Server"
  }
}

# --- Security Group for CI/CD Server ---
resource "aws_security_group" "cicd_sg" {
  name        = "cicd-server-sg"
  description = "Security group for Jenkins and Nexus CI/CD server"

  # SSH Access
  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # Jenkins Web UI
  ingress {
    from_port   = 8080
    to_port     = 8080
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # Nexus Repository Manager
  ingress {
    from_port   = 8081
    to_port     = 8081
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # Outbound Access
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# --- Output Public IP ---
output "cicd_server_public_ip" {
  value       = aws_instance.cicd_server.public_ip
  description = "Public IP address of the Jenkins and Nexus CI/CD server"
}