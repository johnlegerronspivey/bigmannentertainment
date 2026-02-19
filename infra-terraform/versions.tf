terraform {
  backend "s3" {
    bucket  = var.tfstate_bucket
    key     = "${var.project}/${var.env}/terraform.tfstate"
    region  = var.aws_region
    encrypt = true
  }
}
