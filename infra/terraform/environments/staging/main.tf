terraform {
  required_version = ">= 1.6"
  backend "s3" {
    bucket  = "saas-platform-tfstate"
    key     = "staging/terraform.tfstate"
    region  = "us-east-1"
    encrypt = true
  }
}

provider "aws" { region = "us-east-1" }

module "networking" {
  source      = "../../modules/networking"
  environment = "staging"
}

module "database" {
  source         = "../../modules/database"
  environment    = "staging"
  subnet_ids     = module.networking.private_subnets
  vpc_id         = module.networking.vpc_id
  db_password    = var.db_password
  instance_class = "db.t3.small"
}

variable "db_password" { type = string; sensitive = true }
