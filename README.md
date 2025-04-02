# Jackpot IQ Updater

A Python application that scrapes the latest Powerball and Mega Millions lottery numbers from lottery.net and stores them in Firebase.

## Core Functionality

This application performs the following tasks:

- Scrapes the latest Powerball and Mega Millions numbers from lottery.net
- Checks the existing lottery draws in Firebase to determine which draws are new
- Only adds new draws to the database (avoids duplicates)
- Handles both Powerball and Mega Millions draw formats
- Sorts results by date (newest first)
- Processes draws from the current year for efficient scraping

## How It Works

1. The application authenticates with Firebase using credentials stored in Google Cloud Storage
2. It retrieves the latest draw dates for both lottery types from the Firebase database
3. It constructs URLs to scrape the current year's lottery results for both game types
4. For each lottery type, it:
   - Scrapes the webpage and extracts draw dates and numbers
   - Filters out draws already in the database
   - Formats the data appropriately
   - Adds new draws to Firebase

## Data Structure

The application stores data in a `lotteryDraws` Firebase collection with this structure:

```
{
  "date": "YYYY-MM-DD",
  "numbers": [number1, number2, number3, number4, number5],
  "specialBall": number,  // Powerball or Mega Ball number
  "type": "powerball"     // or "mega-millions"
}
```

## Project Structure

- `main.py`: Application entry point
- `lottery_scraper.py`: Main scraping logic and Firebase integration
- `requirements.txt`: Python dependencies

## Environment Variables

- `GCS_BUCKET`: Google Cloud Storage bucket containing Firebase credentials

## Error Handling

The application includes comprehensive error handling for:

- Network issues
- Firebase connection problems
- Google Cloud Storage access issues
- Missing environment variables
- Invalid dates
- Missing or malformed data
- Scraping errors
