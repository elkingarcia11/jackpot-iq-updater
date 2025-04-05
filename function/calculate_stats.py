#!/usr/bin/env python3

import json
import argparse
import os
from collections import defaultdict

# Ensure data directory exists
DATA_DIR = 'data'
os.makedirs(DATA_DIR, exist_ok=True)

def calculate_lottery_stats(mm_input="data/mm.json", 
                           pb_input="data/pb.json",
                           mm_output="data/mm-stats.json", 
                           pb_output="data/pb-stats.json"):
    """
    Calculate comprehensive statistics for lottery draws
    
    Args:
        mm_input (str): Path to the Mega Millions draws JSON file
        pb_input (str): Path to the Powerball draws JSON file
        mm_output (str): Path to save Mega Millions statistics
        pb_output (str): Path to save Powerball statistics
    """
    try:
        # Read the Mega Millions file
        print(f"Reading Mega Millions draws from {mm_input}...")
        with open(mm_input, 'r') as f:
            mm_draws = json.load(f)
        
        # Read the Powerball file
        print(f"Reading Powerball draws from {pb_input}...")
        with open(pb_input, 'r') as f:
            pb_draws = json.load(f)
        
        print(f"Found {len(mm_draws)} Mega Millions draws and {len(pb_draws)} Powerball draws")
        
        # Calculate statistics for Mega Millions
        mm_stats = calculate_stats_for_type(mm_draws, "mega-millions", 
                                           max_regular=70, max_special=25)
        
        # Calculate statistics for Powerball
        pb_stats = calculate_stats_for_type(pb_draws, "powerball", 
                                           max_regular=69, max_special=26)
        
        # Save the statistics to separate files
        with open(mm_output, 'w') as f:
            json.dump(mm_stats, f, indent=2)
        print(f"Saved Mega Millions statistics to {mm_output}")
        
        with open(pb_output, 'w') as f:
            json.dump(pb_stats, f, indent=2)
        print(f"Saved Powerball statistics to {pb_output}")
        
        return True
        
    except Exception as e:
        print(f"Error calculating lottery statistics: {e}")
        import traceback
        traceback.print_exc()
        return False

def calculate_stats_for_type(draws, lottery_type, max_regular, max_special):
    """
    Calculate statistics for a specific lottery type
    
    Args:
        draws (list): List of draw dictionaries
        lottery_type (str): Type of lottery ("powerball" or "mega-millions")
        max_regular (int): Maximum regular number (69 for Powerball, 70 for Mega Millions)
        max_special (int): Maximum special ball number (26 for Powerball, 25 for Mega Millions)
    
    Returns:
        dict: Calculated statistics
    """
    # Initialize counters
    total_draws = len(draws)
    frequency = defaultdict(int)
    frequency_at_position = {
        "0": defaultdict(int),
        "1": defaultdict(int),
        "2": defaultdict(int),
        "3": defaultdict(int),
        "4": defaultdict(int),
        "5": defaultdict(int)  # Special ball position
    }
    special_ball_frequency = defaultdict(int)
    
    # Create a set of existing combinations for fast lookup
    existing_combinations = set()
    
    # Process each draw
    for draw in draws:
        numbers = draw.get("numbers", [])
        special_ball = draw.get("specialBall")
        
        # Create a tuple of the number combination
        if len(numbers) == 5 and special_ball is not None:
            # Sort the regular numbers to normalize the combination
            sorted_numbers = sorted(numbers)
            # Add the combination to our set
            combination = tuple(sorted_numbers + [special_ball])
            existing_combinations.add(combination)
        
        # Count regular numbers frequency (overall)
        for num in numbers:
            frequency[str(num)] += 1
        
        # Count frequency at position
        for i, num in enumerate(numbers):
            if i < 5:  # Make sure we don't exceed our positions
                frequency_at_position[str(i)][str(num)] += 1
        
        # Count special ball frequency
        if special_ball:
            special_ball_frequency[str(special_ball)] += 1
            frequency_at_position["5"][str(special_ball)] += 1
    
    # Ensure all possible numbers are represented in frequency
    for i in range(1, max_regular + 1):
        if str(i) not in frequency:
            frequency[str(i)] = 0
    
    # Ensure all possible special ball numbers are represented
    for i in range(1, max_special + 1):
        if str(i) not in special_ball_frequency:
            special_ball_frequency[str(i)] = 0
    
    # Get sorted frequency lists for each position
    position_frequencies = []
    for pos in range(5):
        pos_str = str(pos)
        # Convert dictionary to list of (number, frequency) tuples
        freq_list = [(int(num), freq) for num, freq in frequency_at_position[pos_str].items()]
        # Sort by frequency (descending)
        freq_list.sort(key=lambda x: x[1], reverse=True)
        position_frequencies.append(freq_list)
    
    # Get sorted special ball frequencies
    special_freq_list = [(int(num), freq) for num, freq in special_ball_frequency.items()]
    special_freq_list.sort(key=lambda x: x[1], reverse=True)
    
    # Calculate optimized winning numbers that don't exist in previous draws
    optimized_numbers = find_optimized_numbers(position_frequencies, special_freq_list, existing_combinations)
    print(f"Found optimized numbers for {lottery_type}: {optimized_numbers}")
    
    # Create the final statistics object
    stats = {
        "type": lottery_type,
        "totalDraws": total_draws,
        "frequency": dict(frequency),
        "frequencyAtPosition": dict(frequency_at_position),
        "specialBallFrequency": dict(special_ball_frequency),
        "optimizedWinningNumber": optimized_numbers
    }
    
    return stats

def find_optimized_numbers(position_frequencies, special_freq_list, existing_combinations):
    """
    Find optimized numbers that don't exist in previous draws
    
    Args:
        position_frequencies (list): List of frequency lists for each position
        special_freq_list (list): Frequency list for special ball
        existing_combinations (set): Set of existing number combinations
    
    Returns:
        list: Optimized winning numbers
    """
    # Try different combinations until we find one that doesn't exist
    
    # Start with top frequency at each position
    attempt = 0
    max_attempts = 1000  # Limit to prevent infinite loops
    
    while attempt < max_attempts:
        # Get the position indices to try
        position_indices = [0, 0, 0, 0, 0, 0]  # Last one is for special ball
        
        # Adjust indices based on attempt number to try different combinations
        if attempt > 0:
            # Use binary representation to create different patterns of indices
            for i in range(6):  # 5 regular positions + 1 special ball
                # Determine which positions to increment
                if attempt & (1 << i):  # Use bits to select positions
                    position_indices[i] = min(1, len(position_frequencies[i]) - 1) if i < 5 else min(1, len(special_freq_list) - 1)
        
        # Get numbers based on current indices
        numbers = []
        for i in range(5):
            if position_frequencies[i] and position_indices[i] < len(position_frequencies[i]):
                numbers.append(position_frequencies[i][position_indices[i]][0])
            else:
                numbers.append(0)  # Fallback
        
        # Get special ball
        if special_freq_list and position_indices[5] < len(special_freq_list):
            special_ball = special_freq_list[position_indices[5]][0]
        else:
            special_ball = 0  # Fallback
        
        # Check if this combination exists in previous draws
        sorted_numbers = sorted(numbers)
        combination = tuple(sorted_numbers + [special_ball])
        
        if combination not in existing_combinations:
            # Found a unique combination
            return numbers + [special_ball]
        
        attempt += 1
    
    # If we couldn't find a unique combination (very unlikely), return the most frequent
    most_frequent = []
    for i in range(5):
        if position_frequencies[i]:
            most_frequent.append(position_frequencies[i][0][0])
        else:
            most_frequent.append(0)
    
    if special_freq_list:
        most_frequent.append(special_freq_list[0][0])
    else:
        most_frequent.append(0)
    
    return most_frequent