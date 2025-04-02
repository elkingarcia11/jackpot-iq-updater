from lottery_scraper import scrape_lottery_data

def scrape_lottery(request):
    """Cloud Function to scrape lottery data"""
    try:
        results = scrape_lottery_data()
        return {
            'status': 'success',
            'powerball_draws': len(results['powerball']),
            'megamillions_draws': len(results['megamillions'])
        }
    except Exception as e:
        return {
            'status': 'error',
            'message': str(e)
        } 