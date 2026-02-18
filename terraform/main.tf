provider "aws" {
  region = "ap-south-1"
}

# VPC-

resource "aws_vpc" "finance_vpc" {
  cidr_block = "10.0.0.0/16"

  tags = {
    Name = "Finance-VPC"
  }
}

resource "aws_subnet" "public_subnet" {
  vpc_id                  = aws_vpc.finance_vpc.id
  cidr_block              = "10.0.1.0/24"
  map_public_ip_on_launch = true
  availability_zone       = "ap-south-1a"

  tags = {
    Name = "Finance-Public-Subnet"
  }
}

resource "aws_internet_gateway" "igw" {
  vpc_id = aws_vpc.finance_vpc.id

  tags = {
    Name = "Finance-IGW"
  }
}

resource "aws_route_table" "public_rt" {
  vpc_id = aws_vpc.finance_vpc.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.igw.id
  }

  tags = {
    Name = "Finance-Public-RT"
  }
}

resource "aws_route_table_association" "public_assoc" {
  subnet_id      = aws_subnet.public_subnet.id
  route_table_id = aws_route_table.public_rt.id
}



resource "aws_security_group" "finance_sg" {
  name   = "finance-sg"
  vpc_id = aws_vpc.finance_vpc.id  
  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 22
    to_port     = 22
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

# EC2 -

resource "aws_instance" "Finance-App-Server" {
  ami           = "ami-0ff5003538b60d5ec"
  instance_type = "t3.micro"
  key_name      = "fin-key"

  subnet_id              = aws_subnet.public_subnet.id
  vpc_security_group_ids = [aws_security_group.finance_sg.id]
  associate_public_ip_address = true


  user_data = <<-EOF
              #!/bin/bash
              yum update -y
              yum install docker -y
              service docker start
              usermod -a -G docker ec2-user
              docker pull purohittarang42/finance-app
              docker run -d --restart always -p 80:8000 purohittarang42/finance-app

              EOF

  tags = {
    Name = "Finance-App-Server"
  }
}
