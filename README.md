# Jackpot IQ Updater

A Python application that scrapes the latest Powerball and Mega Millions lottery numbers, calculates statistics, and synchronizes the data with Google Cloud Storage.

## Core Functionality

This application performs the following tasks:

- Scrapes the latest Powerball and Mega Millions numbers from lottery.net
- Stores draw data in JSON files (both locally and in Google Cloud Storage)
- Calculates comprehensive statistics for each lottery type
- Generates optimized number combinations based on historical data
- Maintains data sorted by date (newest first)
- Handles data synchronization between local storage and cloud storage

## How It Works

1. The application fetches existing lottery draw data from Google Cloud Storage
2. It scrapes the latest lottery numbers from lottery.net
3. New draws are identified and added to the JSON files
4. Statistics are automatically calculated whenever new draws are added
5. All data is synchronized back to Google Cloud Storage
6. The application generates "optimized" number combinations that have never appeared before

## Data Structure

The application stores data in JSON files with this structure:

**Draw Data (`pb.json` and `mm.json`):**

```json
[
  {
    "date": "YYYY-MM-DD",
    "numbers": [number1, number2, number3, number4, number5],
    "specialBall": number,  // Powerball or Mega Ball number
    "type": "powerball"     // or "mega-millions"
  }
]
```

**Statistics (`pb-stats.json` and `mm-stats.json`):**

```json
{
  "type": "powerball",
  "totalDraws": 3629,
  "frequency": {
    "1": 15,
    "2": 30
    // Numbers and their frequencies
  },
  "frequencyAtPosition": {
    "0": {
      /* numbers and frequencies at position 0 */
    },
    "1": {
      /* numbers and frequencies at position 1 */
    }
    // Positions 0-4 for regular numbers, 5 for special ball
  },
  "specialBallFrequency": {
    "1": 15,
    "2": 30
    // Special ball numbers and frequencies
  },
  "optimizedWinningNumber": [1, 15, 27, 39, 45, 20] // Optimized number combination
}
```

## Project Structure

- `function/` - Main application code
  - `main.py` - Application entry point
  - `lottery_scraper.py` - Core scraping and data synchronization logic
  - `calculate_stats.py` - Statistics calculation for lottery draws
  - `requirements.txt` - Python dependencies
- `data/` - Local data directory (created automatically)
  - `pb.json` - Powerball draw data
  - `mm.json` - Mega Millions draw data
  - `pb-stats.json` - Powerball statistics
  - `mm-stats.json` - Mega Millions statistics

## Setup and Installation

1. **Clone the repository:**

   ```bash
   git clone https://github.com/YourUsername/jackpot-iq-updater.git
   cd jackpot-iq-updater
   ```

2. **Create a virtual environment:**

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**

   ```bash
   pip install -r function/requirements.txt
   ```

4. **Set up Google Cloud Authentication:**
   The application uses [Application Default Credentials (ADC)](https://cloud.google.com/docs/authentication/application-default-credentials) to authenticate with Google Cloud Storage. This means:

   - When running locally, it will use your user credentials (configured via the gcloud CLI)
   - When running in Google Cloud, it will use the service account attached to the resource

   To set up local authentication:

   ```bash
   gcloud auth application-default login
   ```

5. **Configure environment variables:**
   - Create a `.env` file based on `.env.example`
   - Set `GCS_BUCKET` to your Google Cloud Storage bucket name (defaults to "jackpot-iq")

## Usage

To run the full lottery data update:

```bash
python function/main.py
```

To only calculate statistics from existing data:

```bash
python function/calculate_stats.py
```

## Environment Variables

- `GCS_BUCKET`: Google Cloud Storage bucket name (default: "jackpot-iq")

## Error Handling

The application includes comprehensive error handling for:

- Network issues during scraping
- Google Cloud Storage access problems
- Invalid or missing data files
- Malformed lottery data
- Authentication failures
- Statistics calculation errors
