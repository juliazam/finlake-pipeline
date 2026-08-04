data "aws_iam_policy_document" "glue_assume_role" {
  statement {
    actions = ["sts:AssumeRole"]
    principals {
      type        = "Service"
      identifiers = ["glue.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "glue_role" {
  name               = "finlake-glue-role"
  assume_role_policy = data.aws_iam_policy_document.glue_assume_role.json
}

data "aws_iam_policy_document" "s3_access" {
  statement {
    actions = ["s3:GetObject", "s3:PutObject", "s3:ListBucket"]
    resources = [
      aws_s3_bucket.finlake_ingest.arn,
      "${aws_s3_bucket.finlake_ingest.arn}/*",
    ]
  }
}

resource "aws_iam_role_policy" "glue_s3_access" {
  name   = "finlake-glue-s3-access"
  role   = aws_iam_role.glue_role.id
  policy = data.aws_iam_policy_document.s3_access.json
}

data "aws_iam_policy_document" "lambda_assume_role" {
  statement {
    actions = ["sts:AssumeRole"]
    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "lambda_role" {
  name               = "finlake-lambda-role"
  assume_role_policy = data.aws_iam_policy_document.lambda_assume_role.json
}

resource "aws_iam_role_policy" "lambda_s3_access" {
  name   = "finlake-lambda-s3-access"
  role   = aws_iam_role.lambda_role.id
  policy = data.aws_iam_policy_document.s3_access.json
}
