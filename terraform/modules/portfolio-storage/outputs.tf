output "bucket_name" {
  description = "Portfolio S3 bucket name"
  value       = aws_s3_bucket.portfolio_assets.id
}

output "bucket_arn" {
  description = "Portfolio S3 bucket ARN"
  value       = aws_s3_bucket.portfolio_assets.arn
}

output "bucket_regional_domain_name" {
  description = "Portfolio S3 bucket regional domain name"
  value       = aws_s3_bucket.portfolio_assets.bucket_regional_domain_name
}

output "thumbnail_bucket_name" {
  description = "Thumbnail S3 bucket name"
  value       = aws_s3_bucket.thumbnails.id
}

output "thumbnail_bucket_arn" {
  description = "Thumbnail S3 bucket ARN"
  value       = aws_s3_bucket.thumbnails.arn
}
