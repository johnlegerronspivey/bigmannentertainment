# Portfolio Storage Module - S3 Buckets for Image Assets

resource "aws_s3_bucket" "portfolio_assets" {
  bucket = "${var.bucket_prefix}-${var.environment}"
  
  tags = merge(var.tags, {
    Name    = "Portfolio Assets"
    Purpose = "ImageStorage"
  })
}

resource "aws_s3_bucket_versioning" "portfolio_versioning" {
  bucket = aws_s3_bucket.portfolio_assets.id
  
  versioning_configuration {
    status = var.enable_versioning ? "Enabled" : "Suspended"
  }
}

resource "aws_s3_bucket_encryption" "portfolio_encryption" {
  bucket = aws_s3_bucket.portfolio_assets.id
  
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_public_access_block" "portfolio_access" {
  bucket = aws_s3_bucket.portfolio_assets.id
  
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_lifecycle_configuration" "portfolio_lifecycle" {
  bucket = aws_s3_bucket.portfolio_assets.id
  
  rule {
    id     = "transition-to-ia"
    status = "Enabled"
    
    transition {
      days          = 90
      storage_class = "STANDARD_IA"
    }
    
    transition {
      days          = 180
      storage_class = "GLACIER"
    }
  }
  
  rule {
    id     = "delete-old-versions"
    status = "Enabled"
    
    noncurrent_version_expiration {
      days = 90
    }
  }
}

resource "aws_s3_bucket_cors_configuration" "portfolio_cors" {
  bucket = aws_s3_bucket.portfolio_assets.id
  
  cors_rule {
    allowed_headers = ["*"]
    allowed_methods = ["GET", "PUT", "POST"]
    allowed_origins = ["*"]  # Restrict in production
    expose_headers  = ["ETag"]
    max_age_seconds = 3000
  }
}

# S3 Bucket for thumbnails
resource "aws_s3_bucket" "thumbnails" {
  bucket = "${var.bucket_prefix}-thumbnails-${var.environment}"
  
  tags = merge(var.tags, {
    Name    = "Portfolio Thumbnails"
    Purpose = "ThumbnailStorage"
  })
}

resource "aws_s3_bucket_encryption" "thumbnail_encryption" {
  bucket = aws_s3_bucket.thumbnails.id
  
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}
