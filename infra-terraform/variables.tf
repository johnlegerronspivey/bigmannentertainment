variable "project" {
  type = string
}

variable "env" {
  type = string
}

variable "aws_region" {
  type    = string
  default = "us-east-1"
}

variable "tfstate_bucket" {
  type = string
}

variable "aws_profile" {
  type    = string
  default = ""
}
