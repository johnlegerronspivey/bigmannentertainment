variable "project" {
  type = string
}

variable "env" {
  type = string
}

variable "campaign_zip" {
  type = string
}

variable "creative_zip" {
  type = string
}

variable "campaigns_table" {
  type = string
}

variable "creatives_table" {
  type = string
}

variable "s3_bucket" {
  type = string
}

variable "campaigns_table_arn" {
  type = string
}

variable "creatives_table_arn" {
  type = string
}

variable "attribution_table_arn" {
  type = string
}

variable "royalties_table_arn" {
  type = string
}

variable "aws_region" {
  type = string
}

variable "tags" {
  type    = map(string)
  default = {}
}
