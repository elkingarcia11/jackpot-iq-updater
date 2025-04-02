import requests
from bs4 import BeautifulSoup
from datetime import datetime
import firebase_admin
from firebase_admin import credentials, firestore
from google.cloud import storage
import tempfile
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def download_credentials():
    """Download Firebase credentials from Google Cloud Storage"""
    try:
        # Create a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.json') as temp_file:
            temp_path = temp_file.name
            
        # Initialize storage client
        storage_client = storage.Client()
        
        # Get bucket name from environment variable
        bucket_name = os.getenv('GCS_BUCKET')
        if not bucket_name:
            raise ValueError("GCS_BUCKET environment variable is not set")
            
        # Get the bucket and blob
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob('firebase-credentials.json')
        
        # Download the credentials file
        blob.download_to_filename(temp_path)
        
        return temp_path
    except Exception as e:
        print(f"Error downloading credentials: {e}")
        return None

def initialize_firebase():
    """Initialize Firebase Admin SDK"""
    try:
        # Download credentials from GCS
        cred_path = download_credentials()
        if not cred_path:
            print("Failed to download Firebase credentials")
            return None
            
        # Initialize Firebase Admin SDK
        cred = credentials.Certificate(cred_path)
        firebase_admin.initialize_app(cred)
        
        # Clean up temporary file
        try:
            os.unlink(cred_path)
        except Exception as e:
            print(f"Warning: Could not delete temporary credentials file: {e}")
            
        return firestore.client()
    except Exception as e:
        print(f"Error initializing Firebase: {e}")
        return None

def get_latest_draws(db):
    """
    Fetch the latest draw dates for both Powerball and Mega Millions from Firebase
    Returns a dictionary with 'powerball' and 'mega-millions' dates
    """
    try:
        # Get the lotteryDraws collection
        draws_ref = db.collection('lotteryDraws')
        
        # Get latest Powerball draw
        powerball_draws = draws_ref.where('type', '==', 'powerball').order_by('date', direction=firestore.Query.DESCENDING).limit(1).get()
        powerball_date = None
        for draw in powerball_draws:
            powerball_date = draw.get('date')
            print(f"Latest Powerball draw: {draw.to_dict()}")
            break
            
        # Get latest Mega Millions draw
        megamillions_draws = draws_ref.where('type', '==', 'mega-millions').order_by('date', direction=firestore.Query.DESCENDING).limit(1).get()
        megamillions_date = None
        for draw in megamillions_draws:
            megamillions_date = draw.get('date')
            print(f"Latest Mega Millions draw: {draw.to_dict()}")
            break
            
        return {
            'powerball': powerball_date,
            'mega-millions': megamillions_date
        }
    except Exception as e:
        print(f"Error fetching latest draws from Firebase: {e}")
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
                    'powerball' if game_type == 'powerball' else 'mega_ball': special_ball_number
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

def scrape_lottery_data():
    """
    Scrape lottery data using the latest draw dates from Firebase.
    """
    try:
        # Initialize Firebase
        db = initialize_firebase()
        if not db:
            print("Failed to initialize Firebase. Cannot proceed with scraping.")
            return None
            
        # Get latest draw dates from Firebase
        latest_draws = get_latest_draws(db)
        
        if not latest_draws['powerball'] or not latest_draws['mega-millions']:
            print("Failed to get latest draw dates from Firebase")
            return None
            
        print(f"\nLatest Powerball draw: {latest_draws['powerball']}")
        print(f"Latest Mega Millions draw: {latest_draws['mega-millions']}\n")
        
        # Extract year from the most recent draw date
        year = latest_draws['powerball'].split('-')[0]
        
        # Construct URLs
        powerball_url = f"https://www.lottery.net/powerball/numbers/{year}"
        megamillions_url = f"https://www.lottery.net/mega-millions/numbers/{year}"
        
        # Process Powerball draws
        print("\nProcessing Powerball draws...")
        print(f"Latest Powerball draw date: {latest_draws['powerball']}")
        print(f"Scraping from: {powerball_url}")
        
        powerball_draws = scrape_lottery_numbers(powerball_url, 'powerball')
        if powerball_draws:
            # Filter draws after the latest draw date
            filtered_powerball = filter_lottery_data(powerball_draws, latest_draws['powerball'])
            if filtered_powerball:
                # Insert filtered draws into Firebase
                for draw in filtered_powerball:
                    try:
                        # Convert to Firebase format
                        firebase_draw = {
                            'date': draw['date'],
                            'numbers': draw['numbers'],
                            'specialBall': draw['powerball'],
                            'type': 'powerball'
                        }
                        # Add to Firebase
                        db.collection('lotteryDraws').add(firebase_draw)
                        print(f"Added Powerball draw for {draw['date']}")
                    except Exception as e:
                        print(f"Error adding Powerball draw {draw['date']}: {e}")
                print(f"Successfully added {len(filtered_powerball)} Powerball draws to Firebase")
        
        # Process Mega Millions draws
        print("\nProcessing Mega Millions draws...")
        print(f"Latest Mega Millions draw date: {latest_draws['mega-millions']}")
        print(f"Scraping from: {megamillions_url}")
        
        megamillions_draws = scrape_lottery_numbers(megamillions_url, 'megamillions')
        if megamillions_draws:
            # Filter draws after the latest draw date
            filtered_megamillions = filter_lottery_data(megamillions_draws, latest_draws['mega-millions'])
            if filtered_megamillions:
                # Insert filtered draws into Firebase
                for draw in filtered_megamillions:
                    try:
                        # Convert to Firebase format
                        firebase_draw = {
                            'date': draw['date'],
                            'numbers': draw['numbers'],
                            'specialBall': draw['mega_ball'],
                            'type': 'mega-millions'
                        }
                        # Add to Firebase
                        db.collection('lotteryDraws').add(firebase_draw)
                        print(f"Added Mega Millions draw for {draw['date']}")
                    except Exception as e:
                        print(f"Error adding Mega Millions draw {draw['date']}: {e}")
                print(f"Successfully added {len(filtered_megamillions)} Mega Millions draws to Firebase")
        
        return {
            'powerball': filtered_powerball if 'filtered_powerball' in locals() else [],
            'megamillions': filtered_megamillions if 'filtered_megamillions' in locals() else []
        }
        
    except Exception as e:
        print(f"Error in scrape_lottery_data: {e}")
        return None

if __name__ == "__main__":
    # Run without a specific date to use Firebase's latest draw dates
    results = scrape_lottery_data() 