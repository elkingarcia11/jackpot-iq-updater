import json
import os
from lottery_scraper import scrape_lottery_data, get_latest_draws, download_from_gcs, upload_to_gcs
from calculate_stats import calculate_lottery_stats
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get bucket name from environment variable or use default
BUCKET_NAME = os.getenv('GCS_BUCKET', 'jackpot-iq')

def main():
    """
    Main function to scrape lottery data and save to JSON files
    """
    print("Starting lottery data scraping...")
    
    # Download existing data from GCS
    print("Downloading files from GCS bucket:", BUCKET_NAME)
    try:
        download_from_gcs()
    except Exception as e:
        print("Error downloading files from GCS:", str(e))
        # Create empty files if they don't exist
        if not os.path.exists("data/mm.json"):
            with open("data/mm.json", "w") as f:
                json.dump([], f)
        if not os.path.exists("data/pb.json"):
            with open("data/pb.json", "w") as f:
                json.dump([], f)
    
    # Get latest draws from files
    latest_draws = get_latest_draws()
    latest_pb_date = latest_draws['powerball']
    latest_mm_date = latest_draws['mega-millions']
    
    print("\nLatest Powerball draw:", latest_pb_date)
    print("Latest Mega Millions draw:", latest_mm_date)
    print("\n")
    
    # Scrape new lottery data
    print("Scraping new lottery data...")
    scrape_lottery_data()
    
    # Calculate and save statistics
    print("\nUpdating statistics based on new draws...")
    mm_stats, pb_stats = calculate_lottery_stats()
    
    # Save stats to files
    with open("data/mm-stats.json", "w") as f:
        json.dump(mm_stats, f, indent=2)
    with open("data/pb-stats.json", "w") as f:
        json.dump(pb_stats, f, indent=2)
    
    # Upload all files to GCS
    print("\nUploading files to GCS bucket:", BUCKET_NAME)
    try:
        upload_to_gcs()
    except Exception as e:
        print("Error uploading files to GCS:", str(e))
    
    print("Scrape and stats update completed successfully")

if __name__ == "__main__":
    main() 