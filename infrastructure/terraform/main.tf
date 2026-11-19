
terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.0"
    }
  }
}

provider "aws" {
  region = "us-east-1"
}

# Read information about our existing EC2 instance.
data "aws_instance" "shopsphere" {
  instance_id = "i-0c0f14b7e1a1af872"
}

# Display the EC2 information.
output "instance_id" {
  value = data.aws_instance.shopsphere.id
}

output "instance_type" {
  value = data.aws_instance.shopsphere.instance_type
}

output "availability_zone" {
  value = data.aws_instance.shopsphere.availability_zone
}

output "instance_state" {
  value = data.aws_instance.shopsphere.instance_state
}
