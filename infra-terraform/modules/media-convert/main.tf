data "aws_partition" "current" {}

resource "aws_iam_role" "mediaconvert_role" {
  name = "${var.project}-${var.env}-mediaconvert-role"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action    = "sts:AssumeRole"
      Effect    = "Allow"
      Principal = { Service = "mediaconvert.amazonaws.com" }
    }]
  })
}

resource "aws_media_convert_queue" "default" {
  name = "${var.project}-${var.env}-mc-queue"
}
