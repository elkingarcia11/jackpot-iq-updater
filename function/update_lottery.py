#!/usr/bin/env python3

import os
import sys
import subprocess
from lottery_scraper import scrape_lottery_data
from calculate_stats import calculate_lottery_stats

def update_lottery_data():
    """
    Complete lottery update process:
    1. Scrape latest lottery data and save to JSON files
    2. Recalculate statistics and optimized numbers
    """
    print("=== LOTTERY DATA UPDATE PROCESS ===")
    
    # Step 1: Scrape latest lottery data
    print("\n=== STEP 1: SCRAPING LATEST LOTTERY DATA ===")
    scrape_results = scrape_lottery_data()
    
    new_pb_draws = len(scrape_results.get('powerball', [])) if scrape_results else 0
    new_mm_draws = len(scrape_results.get('megamillions', [])) if scrape_results else 0
    
    print(f"\nScraping complete. New draws found:")
    print(f"- Powerball: {new_pb_draws} new draws")
    print(f"- Mega Millions: {new_mm_draws} new draws")
    
    # Step 2: Recalculate statistics
    print("\n=== STEP 2: UPDATING STATISTICS ===")
    
    if new_pb_draws > 0 or new_mm_draws > 0 or not (os.path.exists('pb-stats.json') and os.path.exists('mm-stats.json')):
        print("New draws found or stats files don't exist. Recalculating statistics...")
        
        # Calculate statistics with default file names
        calculate_lottery_stats(
            mm_input="mm.json", 
            pb_input="pb.json",
            mm_output="mm-stats.json", 
            pb_output="pb-stats.json"
        )
        
        print("\nStatistics updated successfully.")
        print("- Powerball stats: pb-stats.json")
        print("- Mega Millions stats: mm-stats.json")
    else:
        print("No new draws found and stats files exist. Skipping statistics update.")
    
    print("\n=== UPDATE PROCESS COMPLETED SUCCESSFULLY ===")
    return {
        'new_powerball_draws': new_pb_draws,
        'new_megamillions_draws': new_mm_draws,
        'statistics_updated': new_pb_draws > 0 or new_mm_draws > 0
    }

if __name__ == "__main__":
    update_lottery_data() 