## Infrastructure reprequisites
1. Create a service account at [IAM & Admin](https://console.cloud.google.com/iam-admin/serviceaccounts)
    - Add the following roles: `Cloud Datastore User`, `Cloud Run Service Agent`, `Service Account User`, `Vertex AI Service Agent`.
2. Create a bucket with a unique name `{UNIQUE_BUCKET_NAME}` at [Buckets](https://console.cloud.google.com/storage/)
    - Download buckets credentials file to keep secrets.
3. Create a NoSQL Datastore at [Datastore](https://console.cloud.google.com/datastore/databases)

## API reprequisites
1. Enable the following GCP APIs: `Vertex AI API`, `Cloud Build API`, `Cloud Datastore API`, `Cloud Logging API`, `Cloud Run Admin API`.
2. Sign up for an account at [EdenAI](https://app.edenai.run/) to obtain key `{IMG_API_KEY}` for Image Generator.


## Steps to run
1. Clone this repository.
2. Change directory to `app` by `cd app`.
3. Build container with Cloud Build `gcloud builds submit --timeout=900 --tag gcr.io/{GOOGLE_CLOUD_PROJECT}/{APP_NAME}`
4. Deploy container with Cloud Run `gcloud run deploy final --image gcr.io/{GOOGLE_CLOUD_PROJECT}/{APP_NAME}   --service-account {SERVICE_ACCOUNT}   --region={REGION}   --allow-unauthenticated`
5. Get `Service URL` from [Cloud Run](https://console.cloud.google.com/run) or terminal after a success build.
6. Set up [OAuth Consent Screen](https://console.cloud.google.com/apis/credentials/consent).
7. Create a OAuth 2.0 Key at [Credentials](https://console.cloud.google.com/apis/credentials) and add `Service URL/callback` under `Authorized redirect URIs` section. Obtain the `OAUTH_CLIENT_ID` and `OATH_CLIENT_SECRET`.
8. Update the app environment with `gcloud run services update {APP_NAME}  --update-env-vars REDIRECT_CALLBACK={Service URL}/callback  --update-env-vars CLIENT_ID=OAUTH_CLIENT_ID --update-env-vars CLIENT_SECRET=OATH_CLIENT_SECRET  --update-env-vars BUCKET_NAME={UNIQUE_BUCKET_NAME}  --update-env-vars IMG_API={IMG_API_KEY} --region={REGION}`

## Credits
https://github.com/wu4f/cs430-src

## License
[MIT](LICENSE)