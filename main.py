from google.cloud import bigquery
import functions_framework
import os

# Config
PROJECT_ID = "cloud-composer-487502"
DATASET_ID = "Temp"
TABLE_ID = "student_marks"

@functions_framework.cloud_event
def gcs_to_bq(cloud_event):
    """
    Triggered by a file upload to GCS bucket
    """

    data = cloud_event.data

    bucket_name = data["bucket"]
    file_name = data["name"]

    # Only process CSV files
    if not file_name.endswith(".csv"):
        print(f"Skipping non-CSV file: {file_name}")
        return

    uri = f"gs://{bucket_name}/{file_name}"

    print(f"Processing file: {uri}")

    client = bigquery.Client()

    table_ref = f"{PROJECT_ID}.{DATASET_ID}.{TABLE_ID}"

    job_config = bigquery.LoadJobConfig(
        source_format=bigquery.SourceFormat.CSV,
        skip_leading_rows=1,
        autodetect=True,
        write_disposition="WRITE_APPEND"
    )

    load_job = client.load_table_from_uri(
        uri,
        table_ref,
        job_config=job_config
    )

    load_job.result()

    print(f"Loaded {uri} into {table_ref}")