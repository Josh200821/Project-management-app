variable "environment"    { type = string }
variable "subnet_ids"     { type = list(string) }
variable "vpc_id"         { type = string }
variable "instance_class" { default = "db.t3.medium" }
variable "db_password"    { type = string; sensitive = true }

resource "aws_db_subnet_group" "main" {
  name       = "saas-${var.environment}"
  subnet_ids = var.subnet_ids
}

resource "aws_db_instance" "primary" {
  identifier              = "saas-${var.environment}"
  engine                  = "postgres"
  engine_version          = "16.1"
  instance_class          = var.instance_class
  allocated_storage       = 100
  storage_encrypted       = true
  db_name                 = "saas_platform"
  username                = "postgres"
  password                = var.db_password
  db_subnet_group_name    = aws_db_subnet_group.main.name
  multi_az                = var.environment == "production"
  backup_retention_period = 7
  deletion_protection     = var.environment == "production"
  skip_final_snapshot     = var.environment != "production"
}

output "primary_endpoint" { value = aws_db_instance.primary.endpoint }
