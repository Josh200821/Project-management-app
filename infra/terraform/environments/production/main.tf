terraform {
  required_version = ">= 1.6"
  backend "s3" {
    bucket  = "saas-platform-tfstate"
    key     = "production/terraform.tfstate"
    region  = "us-east-1"
    encrypt = true
  }
}

provider "aws" { region = "us-east-1" }

module "networking" {
  source      = "../../modules/networking"
  environment = "production"
}

module "database" {
  source      = "../../modules/database"
  environment = "production"
  subnet_ids  = module.networking.private_subnets
  vpc_id      = module.networking.vpc_id
  db_password = var.db_password
}

variable "db_password" { type = string; sensitive = true }
