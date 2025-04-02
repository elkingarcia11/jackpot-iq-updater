from lottery_scraper import scrape_lottery_data
import base64
import json

def scrape_lottery(event, context):
    """
    Cloud Function to scrape lottery data triggered by Pub/Sub
    Args:
        event (dict): The dictionary with data specific to this type of event.
                     The `data` field contains the PubsubMessage message.
                     The `attributes` field contains other attributes of the message.
        context (google.cloud.functions.Context): The Cloud Functions event
                 metadata.
    """
    try:
        print(f"Function triggered by Pub/Sub message: {context.event_id}")
        
        # You can process the Pub/Sub message if needed
        if 'data' in event:
            try:
                pubsub_message = base64.b64decode(event['data']).decode('utf-8')
                print(f"Pub/Sub message: {pubsub_message}")
                # You can parse the message as JSON if it contains configuration
                # message_json = json.loads(pubsub_message)
            except Exception as e:
                print(f"Error decoding Pub/Sub message: {e}")
        
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
        print(f"Error in Pub/Sub triggered function: {error_message}")
        return {
            'status': 'error',
            'message': error_message
        } 