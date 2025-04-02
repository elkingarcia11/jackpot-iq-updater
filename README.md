# Lottery Number Scraper

A Python Cloud Function that automatically scrapes Powerball and Mega Millions lottery numbers from lottery.net and stores them in Firebase. The function runs on a schedule using Cloud Scheduler and Pub/Sub, and only adds new draws to the database.

## Features

- Scrapes Powerball and Mega Millions numbers directly from lottery.net
- Automatically tracks latest draw dates in Firebase
- Only adds new draws to the database
- Handles both Powerball and Mega Millions formats
- Sorts results by date (newest first)
- Firebase integration for persistent storage
- Secure credential management using Google Cloud Storage
- Environment variable configuration
- Cloud Build deployment with GitHub Actions integration

## Requirements

- Python 3.6+
- Google Cloud Platform project with:
  - Cloud Functions enabled
  - Cloud Build enabled
  - Cloud Scheduler enabled
  - Firebase Admin SDK access
  - Google Cloud Storage access
  - Container Registry access

## Local Development

1. Clone this repository:

```bash
git clone <repository-url>
cd jackpot-iq-updater
```

2. Create and activate a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install required packages:

```bash
pip install -r function/requirements.txt
```

4. Set up environment variables:

   - Copy `.env.example` to `.env`
   - Update the values in `.env` with your configuration:
     ```
     GCS_BUCKET=your-bucket-name
     ```

## Deployment

### Manual Deployment

1. Set up Google Cloud:

   - Create a Firebase project
   - Generate a service account key (JSON file)
   - Upload the JSON file to `gs://your-bucket-name/firebase-credentials.json`

2. Deploy using Cloud Build:

```bash
gcloud builds submit \
  --config=cloudbuild.yaml \
  --substitutions=_PROJECT_ID=your-project-id,\
                _FUNCTION_NAME=jackpot-iq-updater,\
                _REGION=us-central1,\
                _GCS_BUCKET=your-bucket-name
```

3. Set up Cloud Scheduler with Pub/Sub:

```bash
# First create a Pub/Sub topic
gcloud pubsub topics create lottery-scraper-trigger

# Then create a Cloud Scheduler job
gcloud scheduler jobs create pubsub lottery-scraper-scheduler \
  --schedule="0 10 * * *" \
  --topic=lottery-scraper-trigger \
  --message-body="{\"scrape\": true}" \
  --time-zone="America/New_York"
```

### Automated Deployment with GitHub Actions

1. Set up GitHub Secrets:

   - Go to your repository settings
   - Navigate to Secrets and Variables > Actions
   - Add the following secrets to the `jackpot-iq-updater-env` environment:
     - `GCP_SA_KEY`: Your Google Cloud service account key JSON (from jackpot-iq-updater-sa)
     - `PROJECT_ID`: Your Google Cloud project ID
     - `FUNCTION_NAME`: jackpot-iq-updater
     - `REGION`: Your preferred region (e.g., us-central1)
     - `GCS_BUCKET`: Your Google Cloud Storage bucket name

2. Push to main branch:
   - The GitHub Action will automatically:
     - Build the Docker container
     - Push to Container Registry
     - Deploy to Cloud Functions

## Project Structure

```
/
├── function/                 # Cloud Function code
│   ├── main.py              # Function entry point (Pub/Sub trigger)
│   ├── lottery_scraper.py   # Main scraping logic
│   ├── requirements.txt     # Python dependencies
│   └── Dockerfile          # Container configuration
├── .github/                 # GitHub Actions configuration
│   └── workflows/
│       └── deploy.yml      # Deployment workflow
├── cloudbuild.yaml         # Cloud Build configuration
└── README.md              # Project documentation
```

## Function Response

The function returns a JSON response with the following structure:

```json
{
  "status": "success",
  "powerball_draws": number,
  "megamillions_draws": number
}
```

Or in case of error:

```json
{
  "status": "error",
  "message": "error description"
}
```

## Firebase Data Structure

The function stores data in a `lotteryDraws` collection with the following structure:

```json
{
  "date": "YYYY-MM-DD",
  "numbers": [number1, number2, number3, number4, number5],
  "specialBall": number,  // Powerball or Mega Ball number
  "type": "powerball"     // or "mega-millions"
}
```

## Error Handling

The function includes comprehensive error handling for:

- Network issues
- Firebase connection problems
- Google Cloud Storage access issues
- Missing environment variables
- Invalid dates
- Missing or malformed data
- Scraping errors
- Build and deployment errors

## License

MIT License
