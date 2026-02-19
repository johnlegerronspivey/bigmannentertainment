output "campaigns_table" {
  value = aws_dynamodb_table.campaigns.name
}

output "creatives_table" {
  value = aws_dynamodb_table.creatives.name
}

output "attribution_table" {
  value = aws_dynamodb_table.attribution.name
}

output "royalties_table" {
  value = aws_dynamodb_table.royalties.name
}
