resource "aws_sns_topic" "alerts" {
  name = "${var.project}-${var.env}-alerts"
  tags = var.tags
}

resource "aws_sns_topic_subscription" "email_admin" {
  topic_arn = aws_sns_topic.alerts.arn
  protocol  = "email"
  endpoint  = var.admin_email
}
