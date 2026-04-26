gcloud functions deploy gcs-to-bq-loader `
  --gen2 `
  --runtime python311 `
  --region us-east1 `
  --source . `
  --entry-point gcs_to_bq `
  --trigger-bucket  example-bucket-bq-2 `
  --memory 512MB `
  --timeout 540s `
  --service-account function-to-bq@cloud-composer-487502.iam.gserviceaccount.com