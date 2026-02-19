variable "project" {
  type = string
}

variable "env" {
  type = string
}

variable "initial_secret_json" {
  type    = map(string)
  default = {}
}

variable "tags" {
  type    = map(string)
  default = {}
}
