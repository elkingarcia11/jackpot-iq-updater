from lottery_scraper import scrape_lottery_data

def main():
    """
    Main function to scrape lottery data
    """
    try:
        print("Starting lottery data scraping...")
        
        # Execute the scraping function
        results = scrape_lottery_data()
        
        # Log the results
        if results:
            print(f"Scrape successful. Powerball draws: {len(results['powerball'])}, Mega Millions draws: {len(results['megamillions'])}")
            return {
                'status': 'success',
                'powerball_draws': len(results['powerball']),
                'megamillions_draws': len(results['megamillions'])
            }
        else:
            print("No results returned from scraping function")
            return {'status': 'error', 'message': 'No results returned'}
    except Exception as e:
        error_message = str(e)
        print(f"Error in scraping function: {error_message}")
        return {
            'status': 'error',
            'message': error_message
        }

if __name__ == "__main__":
    main() 