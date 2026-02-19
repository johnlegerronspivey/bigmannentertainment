variable "project" {
  type = string
}

variable "env" {
  type = string
}

variable "trigger_lambda_arn" {
  type = string
}

variable "tags" {
  type    = map(string)
  default = {}
}
