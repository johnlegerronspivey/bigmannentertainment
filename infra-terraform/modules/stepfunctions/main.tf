resource "aws_iam_role" "sfn_role" {
  name               = "${var.project}-${var.env}-sfn-role"
  assume_role_policy = data.aws_iam_policy_document.sfn_assume.json
}

data "aws_iam_policy_document" "sfn_assume" {
  statement {
    actions = ["sts:AssumeRole"]
    principals {
      type        = "Service"
      identifiers = ["states.amazonaws.com"]
    }
  }
}

resource "aws_sfn_state_machine" "workflow" {
  name       = "${var.project}-${var.env}-workflow"
  role_arn   = aws_iam_role.sfn_role.arn
  definition = file(var.definition_json_path)
}
