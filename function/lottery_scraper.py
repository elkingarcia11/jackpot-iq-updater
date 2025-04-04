import requests
from bs4 import BeautifulSoup
from datetime import datetime
import json
import os
from dotenv import load_dotenv
from google.cloud import storage

# Load environment variables
load_dotenv()

# Ensure data directory exists
DATA_DIR = 'data'
os.makedirs(DATA_DIR, exist_ok=True)

# GCS bucket name from environment variable or use default
GCS_BUCKET = os.getenv('GCS_BUCKET', 'jackpot-iq')

def download_from_gcs():
    """
    Download JSON files from Google Cloud Storage using application default credentials
    """
    try:
        print(f"Downloading files from GCS bucket: {GCS_BUCKET}")
        
        # Initialize storage client with default credentials
        storage_client = storage.Client()
        bucket = storage_client.bucket(GCS_BUCKET)
        
        # Files to download
        files = ['mm.json', 'pb.json']
        
        for filename in files:
            local_path = os.path.join(DATA_DIR, filename)
            blob = bucket.blob(f"data/{filename}")
            
            # Check if blob exists
            if blob.exists():
                print(f"Downloading {filename} from GCS...")
                blob.download_to_filename(local_path)
                print(f"Downloaded {filename} to {local_path}")
            else:
                print(f"File {filename} not found in GCS bucket. Will create it if needed.")
                # Create empty file if it doesn't exist locally
                if not os.path.exists(local_path):
                    with open(local_path, 'w') as f:
                        json.dump([], f)
                    print(f"Created empty {local_path}")
        
        return True
        
    except Exception as e:
        print(f"Error downloading files from GCS: {e}")
        # Create empty files if download fails
        for filename in ['mm.json', 'pb.json']:
            local_path = os.path.join(DATA_DIR, filename)
            if not os.path.exists(local_path):
                with open(local_path, 'w') as f:
                    json.dump([], f)
                print(f"Created empty {local_path} after GCS error")
        return False

def upload_to_gcs():
    """
    Upload JSON files to Google Cloud Storage using application default credentials
    """
    try:
        print(f"Uploading files to GCS bucket: {GCS_BUCKET}")
        
        # Initialize storage client with default credentials
        storage_client = storage.Client()
        bucket = storage_client.bucket(GCS_BUCKET)
        
        # Files to upload
        files = ['mm.json', 'pb.json', 'mm-stats.json', 'pb-stats.json']
        
        for filename in files:
            local_path = os.path.join(DATA_DIR, filename)
            
            # Skip if file doesn't exist
            if not os.path.exists(local_path):
                print(f"Warning: {local_path} not found. Skipping upload.")
                continue
            
            blob = bucket.blob(f"data/{filename}")
            blob.upload_from_filename(local_path)
            print(f"Uploaded {local_path} to GCS as data/{filename}")
        
        return True
        
    except Exception as e:
        print(f"Error uploading files to GCS: {e}")
        return False

def get_latest_draws():
    """
    Fetch the latest draw dates from local JSON files (data/pb.json and data/mm.json)
    Returns a dictionary with 'powerball' and 'mega-millions' dates
    """
    try:
        # Default values if files don't exist
        powerball_date = None
        megamillions_date = None
        
        # Try to load Powerball draws
        pb_path = os.path.join(DATA_DIR, 'pb.json')
        if os.path.exists(pb_path):
            with open(pb_path, 'r') as f:
                powerball_draws = json.load(f)
                if powerball_draws and len(powerball_draws) > 0:
                    # Sort by date in descending order to get the latest
                    powerball_draws.sort(key=lambda x: x.get('date', ''), reverse=True)
                    powerball_date = powerball_draws[0].get('date')
                    print(f"Latest Powerball draw: {powerball_draws[0]}")
        
        # Try to load Mega Millions draws
        mm_path = os.path.join(DATA_DIR, 'mm.json')
        if os.path.exists(mm_path):
            with open(mm_path, 'r') as f:
                megamillions_draws = json.load(f)
                if megamillions_draws and len(megamillions_draws) > 0:
                    # Sort by date in descending order to get the latest
                    megamillions_draws.sort(key=lambda x: x.get('date', ''), reverse=True)
                    megamillions_date = megamillions_draws[0].get('date')
                    print(f"Latest Mega Millions draw: {megamillions_draws[0]}")
        
        return {
            'powerball': powerball_date,
            'mega-millions': megamillions_date
        }
    except Exception as e:
        print(f"Error fetching latest draws from JSON files: {e}")
        return {'powerball': None, 'mega-millions': None}

def scrape_lottery_numbers(url, game_type):
    """
    Scrape lottery numbers directly from URL
    game_type: 'powerball' or 'megamillions'
    """
    try:
        # Get webpage content
        response = requests.get(url)
        response.raise_for_status()
        
        # Parse the HTML content
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find all draw entries (they are in table rows)
        draws = []
        
        # Find all table rows that contain draw information
        draw_rows = soup.find_all('tr')
        
        for row in draw_rows:
            try:
                # Find the date cell
                date_cell = row.find('td', style="text-align: center;")
                if not date_cell:
                    continue
                    
                # Extract date from the link
                date_link = date_cell.find('a')
                if not date_link:
                    continue
                    
                date_text = date_link.text.strip()
                # Parse the date (format: "Wednesday March 26, 2025")
                date_parts = date_text.split()
                if len(date_parts) < 3:
                    continue
                    
                # Clean up the date string by removing extra commas
                date_str = f"{date_parts[1]} {date_parts[2].replace(',', '')}, {date_parts[3]}"
                date = datetime.strptime(date_str, '%B %d, %Y').strftime('%Y-%m-%d')
                
                # Find the numbers cell
                numbers_cell = row.find_all('td')[1] if len(row.find_all('td')) > 1 else None
                if not numbers_cell:
                    continue
                
                # Find the first set of numbers (main draw, not double play)
                game_class = 'powerball' if game_type == 'powerball' else 'mega-millions'
                numbers_list = numbers_cell.find('ul', class_=f'multi results {game_class}')
                if not numbers_list:
                    continue
                
                # Extract main numbers
                numbers = numbers_list.find_all('li', class_='ball')
                if len(numbers) < 5:
                    continue
                    
                main_numbers = [int(num.text.strip()) for num in numbers[:5]]
                
                # Extract special ball number (Powerball or Mega Ball)
                special_ball = numbers_list.find('li', class_='powerball' if game_type == 'powerball' else 'mega-ball')
                if not special_ball:
                    continue
                    
                special_ball_number = int(special_ball.text.strip())
                
                draws.append({
                    'date': date,
                    'numbers': main_numbers,
                    'specialBall': special_ball_number,
                    'type': 'powerball' if game_type == 'powerball' else 'mega-millions'
                })
            except Exception as e:
                print(f"Error processing draw entry: {e}")
                continue
        
        return draws
        
    except Exception as e:
        print(f"Error scraping {game_type} data: {e}")
        return None

def filter_lottery_data(data, start_date):
    """Filter lottery data from the day after start_date"""
    try:
        if not start_date:
            # If no start_date provided, return all data
            return data
            
        # Convert start_date string to datetime object
        start_datetime = datetime.strptime(start_date, '%Y-%m-%d')
        
        # Filter draws from the day after start_date (exclusive)
        filtered_data = [
            draw for draw in data 
            if datetime.strptime(draw['date'], '%Y-%m-%d') > start_datetime
        ]
        
        # Sort the filtered data by date in descending order (newest first)
        filtered_data.sort(key=lambda x: x['date'], reverse=True)
        
        return filtered_data
        
    except Exception as e:
        print(f"Error filtering lottery data: {e}")
        return None

def update_statistics():
    """Update statistics based on current JSON data"""
    try:
        from calculate_stats import calculate_lottery_stats
        print("\nUpdating statistics based on new draws...")
        calculate_lottery_stats(
            mm_input=os.path.join(DATA_DIR, "mm.json"), 
            pb_input=os.path.join(DATA_DIR, "pb.json"),
            mm_output=os.path.join(DATA_DIR, "mm-stats.json"), 
            pb_output=os.path.join(DATA_DIR, "pb-stats.json")
        )
        print("Statistics updated successfully")
        return True
    except Exception as e:
        print(f"Error updating statistics: {e}")
        return False

def save_to_json(draws, filename):
    """Save draws to a JSON file in the data directory"""
    try:
        # Get full file path
        file_path = os.path.join(DATA_DIR, filename)
        
        # Track if new draws were added
        new_draws_added = False
        
        # Load existing draws if file exists
        existing_draws = []
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                existing_draws = json.load(f)
        
        # Add new draws to existing draws
        # Create a set of existing dates to avoid duplicates
        existing_dates = {draw.get('date') for draw in existing_draws}
        
        for draw in draws:
            if draw.get('date') not in existing_dates:
                existing_draws.append(draw)
                existing_dates.add(draw.get('date'))
                new_draws_added = True
        
        # Sort draws by date (newest first)
        existing_draws.sort(key=lambda x: x.get('date', ''), reverse=True)
        
        # Save to file
        with open(file_path, 'w') as f:
            json.dump(existing_draws, f, indent=2)
        
        return new_draws_added
    except Exception as e:
        print(f"Error saving to JSON: {e}")
        return False

def scrape_lottery_data():
    """
    Scrape lottery data using the latest draw dates from local JSON files.
    Automatically updates statistics if new draws are added.
    
    Returns:
        dict: Results with new draws
    """
    try:
        # First, download files from GCS
        download_from_gcs()
        
        # Get latest draw dates from JSON files
        latest_draws = get_latest_draws()
        
        # If no draws found, set default dates to start from
        if not latest_draws['powerball']:
            latest_draws['powerball'] = '2020-01-01'
            print(f"No existing Powerball draws found. Starting from {latest_draws['powerball']}")
            
        if not latest_draws['mega-millions']:
            latest_draws['mega-millions'] = '2020-01-01'
            print(f"No existing Mega Millions draws found. Starting from {latest_draws['mega-millions']}")
            
        print(f"\nLatest Powerball draw: {latest_draws['powerball']}")
        print(f"Latest Mega Millions draw: {latest_draws['mega-millions']}\n")
        
        # Extract year from the most recent draw date
        current_year = datetime.now().year
        
        # Construct URLs
        powerball_url = f"https://www.lottery.net/powerball/numbers/{current_year}"
        megamillions_url = f"https://www.lottery.net/mega-millions/numbers/{current_year}"
        
        # Flag to track if any new draws were added
        any_new_draws = False
        
        # Process Powerball draws
        print("\nProcessing Powerball draws...")
        print(f"Latest Powerball draw date: {latest_draws['powerball']}")
        print(f"Scraping from: {powerball_url}")
        
        powerball_draws = scrape_lottery_numbers(powerball_url, 'powerball')
        filtered_powerball = []
        if powerball_draws:
            # Filter draws after the latest draw date
            filtered_powerball = filter_lottery_data(powerball_draws, latest_draws['powerball'])
            if filtered_powerball:
                # Save to JSON file
                new_pb_draws = save_to_json(filtered_powerball, 'pb.json')
                if new_pb_draws:
                    print(f"Successfully added {len(filtered_powerball)} Powerball draws to data/pb.json")
                    any_new_draws = True
                else:
                    print("No new Powerball draws to save")
        
        # Process Mega Millions draws
        print("\nProcessing Mega Millions draws...")
        print(f"Latest Mega Millions draw date: {latest_draws['mega-millions']}")
        print(f"Scraping from: {megamillions_url}")
        
        megamillions_draws = scrape_lottery_numbers(megamillions_url, 'megamillions')
        filtered_megamillions = []
        if megamillions_draws:
            # Filter draws after the latest draw date
            filtered_megamillions = filter_lottery_data(megamillions_draws, latest_draws['mega-millions'])
            if filtered_megamillions:
                # Save to JSON file
                new_mm_draws = save_to_json(filtered_megamillions, 'mm.json')
                if new_mm_draws:
                    print(f"Successfully added {len(filtered_megamillions)} Mega Millions draws to data/mm.json")
                    any_new_draws = True
                else:
                    print("No new Mega Millions draws to save")
        
        # Automatically update statistics if new draws were added
        if any_new_draws:
            update_statistics()
        
        # Upload updated files to GCS
        upload_to_gcs()
        
        return {
            'powerball': filtered_powerball,
            'megamillions': filtered_megamillions
        }
        
    except Exception as e:
        print(f"Error in scrape_lottery_data: {e}")
        return None

if __name__ == "__main__":
    # Run the scraper (automatically updates stats if new draws are found)
    results = scrape_lottery_data()