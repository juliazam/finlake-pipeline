resource "aws_glue_job" "finlake_transform" {
  name     = "finlake-transform-job"
  role_arn = aws_iam_role.glue_role.arn
  command {
    name            = "glueetl"
    script_location = "s3://${aws_s3_bucket.finlake_ingest.id}/${aws_s3_object.glue_script.key}"
    python_version  = "3"
  }
  glue_version      = "5.0"
  number_of_workers = 2
  worker_type       = "G.1X"
}

resource "aws_glue_catalog_database" "finlake_db" {
  name = "finlake_database"
}

resource "aws_glue_crawler" "finlake_processed_crawler" {
  name          = "finlake-processed-crawler"
  role          = aws_iam_role.glue_role.arn
  database_name = aws_glue_catalog_database.finlake_db.name

  s3_target {
    path = "s3://${aws_s3_bucket.finlake_ingest.id}/processed/"
  }
}
