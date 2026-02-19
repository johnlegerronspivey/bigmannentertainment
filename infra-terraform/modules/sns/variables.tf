variable "project" {
  type = string
}

variable "env" {
  type = string
}

variable "admin_email" {
  type = string
}

variable "tags" {
  type    = map(string)
  default = {}
}
