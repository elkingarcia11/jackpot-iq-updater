# Lottery Number Scraper

A Python script that automatically scrapes Powerball and Mega Millions lottery numbers from lottery.net and stores them in Firebase. The script keeps track of the latest draws and only adds new draws to the database.

## Features

- Scrapes Powerball and Mega Millions numbers directly from lottery.net
- Automatically tracks latest draw dates in Firebase
- Only adds new draws to the database
- Handles both Powerball and Mega Millions formats
- Sorts results by date (newest first)
- Firebase integration for persistent storage
- Secure credential management using Google Cloud Storage
- Environment variable configuration

## Requirements

- Python 3.6+
- Google Cloud credentials with access to:
  - Firebase Admin SDK
  - Google Cloud Storage (jackpot-iq bucket)

## Installation

1. Clone this repository:

```bash
git clone <repository-url>
cd jackpot-iq-updater
```

2. Install required packages:

```bash
pip install requests beautifulsoup4 firebase-admin google-cloud-storage python-dotenv
```

3. Set up environment variables:

   - Copy `.env.example` to `.env`
   - Update the values in `.env` with your configuration:
     ```
     GCS_BUCKET=your-bucket-name
     ```

4. Set up Google Cloud:
   - Create a Firebase project
   - Generate a service account key (JSON file)
   - Upload the JSON file to `gs://your-bucket-name/firebase-credentials.json`
   - Ensure your environment has proper Google Cloud credentials

## Usage

Run the script directly:

```bash
python lottery_scraper.py
```

The script will:

1. Load environment variables from `.env`
2. Download Firebase credentials from Google Cloud Storage
3. Connect to Firebase and retrieve the latest draw dates
4. Scrape new lottery draws from lottery.net
5. Filter out draws that are already in the database
6. Add new draws to Firebase

## Firebase Data Structure

The script stores data in a `lotteryDraws` collection with the following structure:

```json
{
  "date": "YYYY-MM-DD",
  "numbers": [number1, number2, number3, number4, number5],
  "specialBall": number,  // Powerball or Mega Ball number
  "type": "powerball"     // or "mega-millions"
}
```

## Error Handling

The script includes comprehensive error handling for:

- Network issues
- Firebase connection problems
- Google Cloud Storage access issues
- Missing environment variables
- Invalid dates
- Missing or malformed data
- Scraping errors

## License

MIT License
