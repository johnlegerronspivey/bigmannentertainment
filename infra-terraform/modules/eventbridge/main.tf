resource "aws_cloudwatch_event_bus" "this" {
  name = "${var.project}-${var.env}-bus"
}

resource "aws_cloudwatch_event_rule" "weather_trigger" {
  name           = "${var.project}-${var.env}-weather-trigger"
  event_bus_name = aws_cloudwatch_event_bus.this.name
  event_pattern = jsonencode({
    "source"      = ["custom.weather"]
    "detail-type" = ["WeatherUpdate"]
  })
}

resource "aws_cloudwatch_event_target" "weather_lambda" {
  rule           = aws_cloudwatch_event_rule.weather_trigger.name
  event_bus_name = aws_cloudwatch_event_bus.this.name
  arn            = var.trigger_lambda_arn
}
