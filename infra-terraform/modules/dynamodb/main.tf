resource "aws_dynamodb_table" "campaigns" {
  name         = "${var.project}-${var.env}-campaigns"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "id"

  attribute {
    name = "id"
    type = "S"
  }

  tags = var.tags
}

resource "aws_dynamodb_table" "creatives" {
  name         = "${var.project}-${var.env}-creatives"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "id"

  attribute {
    name = "id"
    type = "S"
  }

  tags = var.tags
}

resource "aws_dynamodb_table" "attribution" {
  name         = "${var.project}-${var.env}-attribution"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "id"
  range_key    = "campaignId"

  attribute {
    name = "id"
    type = "S"
  }

  attribute {
    name = "campaignId"
    type = "S"
  }

  tags = var.tags
}

resource "aws_dynamodb_table" "royalties" {
  name         = "${var.project}-${var.env}-royalties"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "id"

  attribute {
    name = "id"
    type = "S"
  }

  tags = var.tags
}
