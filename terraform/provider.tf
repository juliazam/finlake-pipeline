terraform {
  required_version = ">= 1.15.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }

    archive = {
      source  = "hashicorp/archive"
      version = "~> 2.4"
    }
  }

  backend "s3" {
    bucket       = "finlake-terraform-state"
    key          = "finlake-pipeline/terraform.tfstate"
    region       = "us-east-1"
    use_lockfile = true

    endpoints = {
      s3 = "http://ministack:4566"
    }

    skip_credentials_validation = true
    skip_requesting_account_id  = true
    use_path_style              = true
    access_key                  = "test"
    secret_key                  = "test"
  }
}

provider "aws" {
  region                      = "us-east-1"
  access_key                  = "test"
  secret_key                  = "test"
  s3_use_path_style           = true
  skip_credentials_validation = true
  skip_metadata_api_check     = true

  endpoints {
    s3     = "http://ministack:4566"
    glue   = "http://ministack:4566"
    sts    = "http://ministack:4566"
    lambda = "http://ministack:4566"
    iam    = "http://ministack:4566"
  }
}