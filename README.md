# FinLake Pipeline

Production-ready data pipeline for a fictional fintech company in Singapore. Ingests daily transaction files from S3, transforms them via AWS Glue, and loads the result into PostgreSQL — fully orchestrated with Apache Airflow and provisioned with Terraform.

[![Docker](https://img.shields.io/badge/Docker-2496ED?logo=docker&logoColor=fff)](#)
[![Python](https://img.shields.io/badge/Python-3776AB?logo=python&logoColor=fff)](#)
[![Postgres](https://img.shields.io/badge/Postgres-%23316192.svg?logo=postgresql&logoColor=white)](#)
[![Alembic](https://img.shields.io/badge/Alembic-red)](#)
[![Terraform](https://img.shields.io/badge/Terraform-844FBA?logo=terraform&logoColor=fff)](#)
[![AWS Lambda](https://custom-icon-badges.demolab.com/badge/AWS%20Lambda-%23FF9900.svg?logo=aws-lambda&logoColor=white)](#)
[![Apache Airflow](https://img.shields.io/badge/Apache%20Airflow-017CEE?logo=apacheairflow&logoColor=fff)](#)
[![Apache Spark](https://img.shields.io/badge/Apache%20Spark-E25A1C?logo=apachespark&logoColor=fff)](#)
[![Slack](https://img.shields.io/badge/Slack-4A154B?logo=slack&logoColor=fff)](#)

## Architecture
```
    S3 (raw file)
            ↓
    Airflow Sensor
            ↓
    AWS Glue Job (Spark transform)
            ↓
    S3 (processed file)
            ↓
    Airflow Sensor → PostgreSQL
```
Alerting (Slack) fires on task failure or when the DAG exceeds its deadline.

## Stack

- **Orchestration:** Apache Airflow 3.3 (TaskFlow API, S3KeySensor, GlueJobOperator)
- **Infrastructure as Code:** Terraform (S3, Glue Job/Crawler/Catalog, Lambda, IAM, remote state with S3 native locking)
- **AWS emulation:** MiniStack (local AWS service emulator)
- **Database:** PostgreSQL 16 + Alembic migrations
- **Transformation:** AWS Glue (Spark), tested locally via the official `aws-glue-libs` Docker image
- **CI/CD:** GitHub Actions (Terraform fmt/validate/plan/apply)

## Project structure
```
├── alembic/ # Database migrations
├── dags/ # Airflow DAG
├── glue/ # Glue transformation script
├── lambda/ # Demo Lambda (S3 event notification)
├── models/ # SQLAlchemy models
├── terraform/ # Infrastructure as code
├── docker-compose.yml
└── Dockerfile # Migration runner image
```

## Running locally

1. Copy `.env.example` to `.env` and `.env.local.example` to `.env.local`, fill in values.
2. Start everything:
```bash
   docker compose up -d
```
   This automatically runs database migrations, provisions AWS infrastructure via Terraform, and starts Airflow (webserver, scheduler, dag-processor).

3. Airflow UI: `http://localhost:8080` (default admin/admin, set during init)
4. A sample raw file is included at `glue/test_data_raw.csv` — schema: `transaction_id, account_id, amount, currency, status, merchant, payment_method, timestamp`. Upload it to today's date partition and trigger the DAG:
```bash
   aws --endpoint-url=http://localhost:4566 s3 cp glue/test_data_raw.csv \
     s3://finlake-ingest-bucket/exports/<today's date>/data.csv --checksum-algorithm SHA256
```
5. Trigger `finlake_ingest_pipeline` in the Airflow UI.

## Known limitations

- **MiniStack does not execute real Spark jobs.** `aws_glue_job` and `GlueJobOperator` demonstrate real infrastructure provisioning and orchestration (API calls, polling, status checks), but the actual data transformation must be run manually against the official `aws-glue-libs` Docker image (see `docker compose --profile manual run glue-transform-test`) and the output uploaded to the `processed/` prefix.
- **AWS provider pinned to `~> 5.0`.** Provider v6.23+ introduced an S3 Control tagging call (`ListTagsForResource`) that MiniStack does not emulate, causing `AccessDenied` errors on `plan`/`apply`.
- **IAM roles are provisioned but not enforced** — MiniStack does not validate permissions the way real AWS IAM does.
- **Sample data is small (3 rows)**, intended to demonstrate the pipeline end-to-end rather than at production volume.