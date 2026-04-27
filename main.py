from google.cloud import bigquery, storage
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
    storage_client = storage.Client()

    table_ref = f"{PROJECT_ID}.{DATASET_ID}.{TABLE_ID}"

    job_config = bigquery.LoadJobConfig(
        source_format=bigquery.SourceFormat.CSV,
        skip_leading_rows=1,
        autodetect=True,
        write_disposition="WRITE_APPEND"
    )

    try:
        load_job = client.load_table_from_uri(
            uri,
            table_ref,
            job_config=job_config
        )

        load_job.result()

        print(f"Loaded {uri} into {table_ref}")

        # Move the processed file to the success folder
        _move_blob(storage_client, bucket_name, file_name, "processed_success")

    except Exception as e:
        print(f"Failed to load {uri} into {table_ref}: {e}")

        # Move the failed file to the failed folder
        try:
            _move_blob(storage_client, bucket_name, file_name, "failed")
        except Exception as move_err:
            print(f"Failed to move failed file: {move_err}")

        return


def _move_blob(storage_client, bucket_name, source_blob_name, dest_prefix):
    """Copy the blob to dest_prefix/<basename> and delete the original."""
    bucket = storage_client.bucket(bucket_name)
    source_blob = bucket.blob(source_blob_name)

    destination_blob_name = f"{dest_prefix.rstrip('/')}/{os.path.basename(source_blob_name)}"

    # Copy then delete (move)
    bucket.copy_blob(source_blob, bucket, destination_blob_name)
    source_blob.delete()

    print(f"Moved gs://{bucket_name}/{source_blob_name} to gs://{bucket_name}/{destination_blob_name}")