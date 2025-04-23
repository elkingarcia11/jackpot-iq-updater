# Jackpot IQ Updater

A Python application that scrapes lottery data (Powerball and Mega Millions), calculates statistical significance, and stores the results in Google Cloud Storage.

## Project Structure

```
jackpot-iq-updater/
├── function/
│   ├── main.py                 # Main script orchestrating the workflow
│   ├── lottery_scraper.py      # Handles data scraping and GCS operations
│   ├── calculate_stats.py      # Calculates lottery statistics and significance
│   ├── data/                   # Local storage for JSON files
│   │   ├── mm.json            # Mega Millions draw history
│   │   ├── pb.json            # Powerball draw history
│   │   ├── mm-stats.json      # Mega Millions statistics
│   │   └── pb-stats.json      # Powerball statistics
│   └── gcs_credentials.json    # Google Cloud Storage credentials
└── .env                        # Environment variables
```

## Data Formats

### Draw History Format (mm.json, pb.json)

```json
[
    {
        "date": "YYYY-MM-DD",
        "numbers": [int, int, int, int, int],
        "specialBall": int,
        "type": "mega-millions" or "powerball"
    },
    ...
]
```

### Statistics Format (mm-stats.json, pb-stats.json)

```json
{
    "type": "powerball" or "mega-millions",
    "totalDraws": int,
    "optimizedByPosition": [int, int, int, int, int, int],
    "optimizedByGeneralFrequency": [int, int, int, int, int, int],
    "regularNumbers": {
        "1": {
            "observed": int,
            "expected": float,
            "residual": float,
            "significant": boolean
        },
        ...
    },
    "specialBallNumbers": {
        "1": {
            "observed": int,
            "expected": float,
            "residual": float,
            "significant": boolean
        },
        ...
    },
    "byPosition": {
        "position0": {
            "1": {
                "observed": int,
                "expected": float,
                "residual": float,
                "significant": boolean
            },
            ...
        },
        ...
    }
}
```

## Statistical Analysis

### Frequency Analysis

- Regular numbers: Counts frequency of each number across all positions
- Special ball: Counts frequency of each special ball number
- Position-specific: Counts frequency of each number at each position (0-4)

### Statistical Significance

- Calculates standardized residuals for each number
- A number is considered statistically significant if |residual| > 2.0 (95% confidence)
- Expected frequencies are calculated assuming uniform distribution

### Optimized Numbers

- `optimizedByPosition`: Most frequent numbers at each position
- `optimizedByGeneralFrequency`: Most frequent numbers overall

## Setup

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Set up environment variables in `.env`:

```
GCS_BUCKET=your-bucket-name
```

3. Place GCS credentials in `function/gcs_credentials.json`

## Usage

Run the main script:

```bash
cd function
export GOOGLE_APPLICATION_CREDENTIALS="gcs_credentials.json"
python main.py
```

## Workflow

1. Downloads existing data from GCS
2. Scrapes latest lottery draws
3. Validates and filters draws:
   - Regular numbers must be within valid range (1-70 for MM, 1-69 for PB)
   - Special ball must be within valid range (1-25 for MM, 1-26 for PB)
4. Calculates statistics:
   - Frequency counts
   - Statistical significance
   - Optimized numbers
5. Uploads updated data to GCS

## Validation

The script performs several validations:

- Draw structure validation
- Number range validation
- Frequency sum checks:
  - Each position should sum to totalDraws
  - Special ball frequencies should sum to totalDraws
  - Regular number frequencies should sum to totalDraws \* 5
