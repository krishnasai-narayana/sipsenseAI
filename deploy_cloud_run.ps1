# Deploy SipSense AI to Google Cloud Run
$PROJECT_ID = "sipsense-ai-demo"
$REGION = "asia-south1"
$SERVICE_NAME = "sipsense-app"
$INSTANCE_CONNECTION = "sipsense-ai-demo:asia-south1:sipsense-pg"

Write-Host "Deploying SipSense AI to Google Cloud Run ($REGION)..." -ForegroundColor Cyan

gcloud run deploy $SERVICE_NAME `
  --source . `
  --project $PROJECT_ID `
  --region $REGION `
  --platform managed `
  --allow-unauthenticated `
  --add-cloudsql-instances $INSTANCE_CONNECTION `
  --set-env-vars "PROJECT_ID=$PROJECT_ID,REGION=$REGION,VERTEX_LOCATION=us-central1,INSTANCE_CONNECTION_NAME=$INSTANCE_CONNECTION,DB_NAME=sipsense,DB_USER=sipsense_app,DB_PASSWORD=Asdf@6891,GEMINI_MODEL=gemini-2.5-flash"
