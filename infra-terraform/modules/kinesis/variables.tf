variable "project" {
  type = string
}

variable "env" {
  type = string
}

variable "shard_count" {
  type    = number
  default = 2
}

variable "retention_hours" {
  type    = number
  default = 24
}

variable "tags" {
  type    = map(string)
  default = {}
}
