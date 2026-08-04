import io
import os
import csv
from datetime import datetime, timedelta
import requests
from airflow.sdk import dag, get_current_context, task, DeadlineAlert, DeadlineReference, SyncCallback
from airflow.providers.amazon.aws.sensors.s3 import S3KeySensor
from airflow.providers.amazon.aws.operators.glue import GlueJobOperator
from airflow.providers.amazon.aws.hooks.s3 import S3Hook
from airflow.providers.postgres.hooks.postgres import PostgresHook

DAG_ID = 'finlake_ingest_pipeline'

def push_found_path(files_list):
    """
    files_list: sonsor automatically sends list of file as metadata.
    """
    # 1. Get context for current task
    context = get_current_context()
    ti = context['ti']

    # 2. Get bucket key that was checked by sensor
    task_instance = ti.task
    bucket_key = task_instance.bucket_key

    # 3. Push value into XCom
    ti.xcom_push(key='data_file_path', value=bucket_key)

    # Return True for sensor
    return True


def push_processed_path(files_list):
    """
    files_list: sonsor automatically sends list of file as metadata.
    """
    # 1. Get context for current task
    context = get_current_context()
    ti = context['ti']

    # 2. Get bucket key that was checked by sensor
    task_instance = ti.task
    bucket_key = task_instance.bucket_key
    bucket_name = task_instance.bucket_name

    # 3. Push value into XCom
    full_path = f"s3://{bucket_name}/{bucket_key}"
    ti.xcom_push(key='processed_data_file_path', value=full_path)

    # Return True for sensor
    return True


def notify_failure(context):
    task_id = context['task_instance'].task_id
    dag_id = context['dag'].dag_id
    exception = context.get('exception')
    message = {
        "text": f"❌ *{dag_id}* — task `{task_id}` failed\n```{exception}```"
    }
    webhook_url = os.environ.get('SLACK_WEBHOOK_URL')
    if webhook_url:
        requests.post(webhook_url, json=message, timeout=10)
    else:
        print(f"SLACK_WEBHOOK_URL not set. Would have sent: {message}")

def notify_deadline_missed(**kwargs):
    context = kwargs.get("context", {})
    dag_id = context.get('dag_run', {}).get('dag_id', DAG_ID)
    message = {
        "text": f"⏰ *{dag_id}* — DAG did not complete within the deadline"
    }
    webhook_url = os.environ.get('SLACK_WEBHOOK_URL')
    if webhook_url:
        requests.post(webhook_url, json=message, timeout=10)
    else:
        print(f"SLACK_WEBHOOK_URL not set. Would have sent: {message}")

@dag(
    dag_id=DAG_ID,
    schedule='@daily',
    start_date=datetime(2026, 1, 1),
    catchup=False,
    default_args={'on_failure_callback': notify_failure},
    deadline=DeadlineAlert(
        reference=DeadlineReference.DAGRUN_LOGICAL_DATE,
        interval=timedelta(minutes=15),
        callback=SyncCallback(notify_deadline_missed),
    ),
)
def finlake_ingest():
    trigger_glue_job = GlueJobOperator(
        task_id='trigger-finlake-transform-job',
        job_name='finlake-transform-job',
        script_args={
            '--data_file_path': '{{ ti.xcom_pull(task_ids="wait_for_daily_report", key="data_file_path") }}',
            '--output_path': 's3://finlake-ingest-bucket/processed/{{ ds }}/data.csv',
        },
        aws_conn_id='aws_default',
        region_name='us-east-1',
        wait_for_completion=True,
    )

    wait_for_daily_report = S3KeySensor(
        task_id='wait_for_daily_report',
        bucket_name='finlake-ingest-bucket',
        bucket_key='exports/{{ ds }}/data.csv',
        aws_conn_id='aws_default',
        poke_interval=30,
        timeout=600,
        mode='reschedule',
        check_fn=push_found_path,
    )

    wait_for_processed_file = S3KeySensor(
        task_id='wait_for_processed_file',
        bucket_name='finlake-ingest-bucket',
        bucket_key='processed/{{ ds }}/data.csv',
        aws_conn_id='aws_default',
        poke_interval=30,
        timeout=1800,  # we have manual step here, so timeout is longer
        mode='reschedule',
        check_fn=push_processed_path
    )

    @task
    def load_to_postgres():
        context = get_current_context()
        ti = context['ti']
        processed_path = ti.xcom_pull(
            task_ids="wait_for_processed_file", key="processed_data_file_path")

        s3_hook = S3Hook(aws_conn_id='aws_default')
        bucket_name, bucket_key = processed_path.replace('s3://', '').split('/', 1)

        file_content = s3_hook.read_key(key=bucket_key, bucket_name=bucket_name)
        reader = csv.DictReader(io.StringIO(file_content))

        pg_hook = PostgresHook(postgres_conn_id='postgres_default')
        rows = [
            (row['transaction_id'], row['account_id'], row['amount'], row['currency'],
            row['status'], row['merchant'], row['payment_method'], row['created_at'])
            for row in reader
        ]

        pg_hook.insert_rows(
            table='transactions',
            rows=rows,
            target_fields=['transaction_id', 'account_id', 'amount', 'currency',
                            'status', 'merchant', 'payment_method', 'created_at'],
            replace=True,
            replace_index='transaction_id',
        )

    wait_for_daily_report >> trigger_glue_job >> wait_for_processed_file >> load_to_postgres()

finlake_ingest()
