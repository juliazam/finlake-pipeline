resource "aws_s3_bucket" "finlake_ingest" {
  bucket = "finlake-ingest-bucket"
}

resource "aws_s3_object" "glue_script" {
  bucket = aws_s3_bucket.finlake_ingest.id
  key    = "scripts/transform_job.py"
  source = "../glue/transform_job.py"
  etag   = filemd5("../glue/transform_job.py")
}

resource "aws_s3_bucket" "terraform_state" {
  bucket = "finlake-terraform-state"
}