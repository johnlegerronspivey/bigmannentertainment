output "stream_name" {
  value = aws_kinesis_stream.impressions.name
}

output "stream_arn" {
  value = aws_kinesis_stream.impressions.arn
}
