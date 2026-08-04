data "archive_file" "s3_notifier_zip" {
  type        = "zip"
  source_file = "../lambda/handler.py"
  output_path = "../lambda/handler.zip"
}

resource "aws_lambda_function" "s3_notifier" {
  function_name    = "finlake-s3-notifier"
  role             = aws_iam_role.lambda_role.arn
  handler          = "handler.handler"
  runtime          = "python3.12"
  filename         = data.archive_file.s3_notifier_zip.output_path
  source_code_hash = data.archive_file.s3_notifier_zip.output_base64sha256
}

resource "aws_lambda_permission" "allow_s3" {
  statement_id  = "AllowS3Invoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.s3_notifier.function_name
  principal     = "s3.amazonaws.com"
  source_arn    = aws_s3_bucket.finlake_ingest.arn
}

resource "aws_s3_bucket_notification" "bucket_notification" {
  bucket = aws_s3_bucket.finlake_ingest.id

  lambda_function {
    lambda_function_arn = aws_lambda_function.s3_notifier.arn
    events              = ["s3:ObjectCreated:*"]
  }

  depends_on = [aws_lambda_permission.allow_s3]
}