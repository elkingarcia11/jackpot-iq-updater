#!/usr/bin/env python3

import json
import argparse
import os
from collections import defaultdict

# Ensure data directory exists
DATA_DIR = 'data'
os.makedirs(DATA_DIR, exist_ok=True)

def verify_frequency_stats(stats):
    """
    Verify that all frequency statistics are correct and consistent
    
    Args:
        stats (dict): Calculated statistics
        
    Returns:
        bool: True if all validations pass, False otherwise
    """
    print(f"\nVerifying frequency statistics for {stats['type']}:")
    all_validations_passed = True
    
    # Get the key data
    total_draws = stats['totalDraws']
    frequency = stats['frequency']
    frequency_at_position = stats['frequencyAtPosition']
    special_ball_frequency = stats['specialBallFrequency']
    
    # 1. Verify that the sum of overall frequencies equals totalDraws * 5
    total_frequency_sum = sum(int(freq) for freq in frequency.values())
    expected_sum = total_draws * 5
    if total_frequency_sum != expected_sum:
        print(f"  FAIL: Total frequency sum ({total_frequency_sum}) != expected sum ({expected_sum})")
        all_validations_passed = False
    else:
        print(f"  PASS: Total frequency sum equals totalDraws * 5 ({total_frequency_sum})")
    
    # 2. Verify that the sum of special ball frequencies equals totalDraws
    special_ball_sum = sum(int(freq) for freq in special_ball_frequency.values())
    if special_ball_sum != total_draws:
        print(f"  FAIL: Special ball frequency sum ({special_ball_sum}) != totalDraws ({total_draws})")
        all_validations_passed = False
    else:
        print(f"  PASS: Special ball frequency sum equals totalDraws ({total_draws})")
    
    # 3. Verify that each position's frequencies sum to totalDraws
    for pos in range(6):  # 0-4 for regular numbers, 5 for special ball
        pos_str = str(pos)
        pos_freq_sum = sum(int(freq) for freq in frequency_at_position[pos_str].values())
        
        if pos_freq_sum != total_draws:
            print(f"  FAIL: Position {pos} frequency sum ({pos_freq_sum}) != totalDraws ({total_draws})")
            all_validations_passed = False
        else:
            print(f"  PASS: Position {pos} frequency sum equals totalDraws ({total_draws})")
    
    # 4. Verify that position 5 frequencies match special ball frequencies
    pos5_freq = frequency_at_position["5"]
    if pos5_freq != special_ball_frequency:
        print(f"  FAIL: Position 5 frequencies don't match special ball frequencies")
        all_validations_passed = False
    else:
        print(f"  PASS: Position 5 frequencies match special ball frequencies")
    
    # 5. Verify that the sum of frequencies at positions 0-4 for each number equals the overall frequency
    for num, freq in frequency.items():
        pos_sum = 0
        for pos in range(5):  # Check positions 0-4
            pos_str = str(pos)
            pos_sum += int(frequency_at_position[pos_str].get(num, 0))
        
        if pos_sum != int(freq):
            print(f"  FAIL: Sum of positions 0-4 for number {num} ({pos_sum}) != overall frequency ({freq})")
            all_validations_passed = False
    
    # Only print this if no issues were found in check #5
    if all_validations_passed:
        print(f"  PASS: Sum of positions 0-4 for each number equals overall frequency")
    
    # 6. Verify that frequency dictionaries are properly sorted (descending)
    for pos_str in frequency_at_position:
        pos_freq = frequency_at_position[pos_str]
        prev_freq = float('inf')
        for _, freq in pos_freq.items():
            if int(freq) > prev_freq:
                print(f"  FAIL: Position {pos_str} frequencies not sorted in descending order")
                all_validations_passed = False
                break
            prev_freq = int(freq)
    
    # Only print this if no issues were found in check #6
    if all_validations_passed:
        print(f"  PASS: All frequency dictionaries are properly sorted in descending order")
    
    return all_validations_passed

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
        
        # Verify all frequency statistics
        print("\nVerifying all frequency statistics...")
        mm_verified = verify_frequency_stats(mm_stats)
        pb_verified = verify_frequency_stats(pb_stats)
        
        if mm_verified and pb_verified:
            print("\nAll frequency statistics verified successfully!")
        else:
            print("\nWARNING: Some frequency statistics verification failed. Check the logs above.")
        
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

def sort_frequency_dict(freq_dict):
    """
    Sort a frequency dictionary by frequency (descending)
    
    Args:
        freq_dict (dict): Dictionary of number -> frequency
        
    Returns:
        dict: Sorted dictionary with most frequent numbers first
    """
    # Convert to list of tuples, sort by frequency (descending)
    sorted_items = sorted(freq_dict.items(), key=lambda x: int(x[1]), reverse=True)
    
    # Convert back to dictionary (maintaining order in Python 3.7+)
    return {k: v for k, v in sorted_items}

def find_optimized_numbers(position_frequencies, special_ball_frequencies, existing_combinations):
    """
    Find optimized numbers based on frequency at position
    
    Args:
        position_frequencies (list): List of frequency lists for each position
        special_ball_frequencies (list): List of frequency tuples for special ball
        existing_combinations (set): Set of existing combinations
    
    Returns:
        list: Optimized winning numbers [regular1, regular2, regular3, regular4, regular5, special]
    """
    # Get the most frequent number at each position
    optimized = []
    for pos_freq in position_frequencies:
        if pos_freq:  # Check if we have any frequencies for this position
            optimized.append(pos_freq[0][0])  # Add the most frequent number
        else:
            optimized.append(1)  # Default to 1 if no data available
    
    # Get the most frequent special ball
    best_special_ball = special_ball_frequencies[0][0] if special_ball_frequencies else 1
    
    # Create a set of just the regular number combinations (without special ball)
    # to check if this exact set of 5 regular numbers has appeared before
    existing_regular_sets = set()
    for combo in existing_combinations:
        existing_regular_sets.add(tuple(sorted(combo[:5])))
    
    # Check if this set of regular numbers already exists
    # If it does, try to substitute with next most frequent numbers
    sorted_regular = sorted(optimized[:5])
    regular_set = tuple(sorted_regular)
    
    attempts = 0
    max_attempts = 100  # Limit to prevent infinite loops
    
    while regular_set in existing_regular_sets and attempts < max_attempts:
        # Try replacing one of the numbers with the next most frequent at that position
        position_to_change = attempts % 5  # Cycle through regular number positions
        
        freq_list = position_frequencies[position_to_change]
        # Find index of current number in the frequency list
        current_num = optimized[position_to_change]
        try:
            current_index = [num for num, _ in freq_list].index(current_num)
            # Use the next number if available
            if current_index + 1 < len(freq_list):
                optimized[position_to_change] = freq_list[current_index + 1][0]
            else:
                # If we've exhausted the list, try a number we haven't used
                used_numbers = set(optimized[:5])
                for i in range(1, 70):  # Assume max is 69 or 70
                    if i not in used_numbers:
                        optimized[position_to_change] = i
                        break
        except ValueError:
            # If we can't find the current number, just increment it
            optimized[position_to_change] = (current_num % 69) + 1
        
        # Recalculate the sorted regular numbers
        sorted_regular = sorted(optimized[:5])
        regular_set = tuple(sorted_regular)
        
        attempts += 1
    
    # Always use the most frequent special ball
    # Return the optimized 5 regular numbers + best special ball
    return sorted_regular + [best_special_ball]

def find_optimized_numbers_by_general_frequency(frequency, special_ball_frequency, existing_combinations, max_regular):
    """
    Find optimized numbers based on general frequency (not position-specific)
    
    Args:
        frequency (dict): Dictionary of number frequencies across all positions
        special_ball_frequency (dict): Dictionary of special ball frequencies
        existing_combinations (set): Set of existing combinations
        max_regular (int): Maximum regular number value
        
    Returns:
        list: Optimized winning numbers [regular1, regular2, regular3, regular4, regular5, special]
    """
    # Convert frequency dict to list of tuples and sort by frequency (descending)
    freq_list = [(int(num), int(freq)) for num, freq in frequency.items()]
    freq_list.sort(key=lambda x: x[1], reverse=True)
    
    # Convert special ball frequency dict to list and sort
    special_freq_list = [(int(num), int(freq)) for num, freq in special_ball_frequency.items()]
    special_freq_list.sort(key=lambda x: x[1], reverse=True)
    
    # Take the top 5 most frequent regular numbers
    optimized_regular = [freq_list[i][0] for i in range(min(5, len(freq_list)))]
    
    # Always take the most frequent special ball
    best_special_ball = special_freq_list[0][0] if special_freq_list else 1
    
    # Sort the regular numbers
    optimized_regular.sort()
    
    # Create a set of just the regular number combinations (without special ball)
    # to check if this exact set of 5 regular numbers has appeared before
    existing_regular_sets = set()
    for combo in existing_combinations:
        existing_regular_sets.add(tuple(sorted(combo[:5])))
    
    # Check if this set of regular numbers already exists
    regular_set = tuple(optimized_regular)
    
    attempts = 0
    max_attempts = 100  # Limit to prevent infinite loops
    
    while regular_set in existing_regular_sets and attempts < max_attempts:
        # Try replacing one of the regular numbers with the next most frequent
        if attempts < len(freq_list) - 5:
            # Replace the least frequent number in our current set with the next most frequent
            # from our overall frequency list that we haven't used yet
            next_best_index = 5 + attempts
            if next_best_index < len(freq_list):
                next_best_number = freq_list[next_best_index][0]
                
                # Find the least frequent number in our current selection
                least_frequent_idx = 0
                least_frequent_val = float('inf')
                
                for i, num in enumerate(optimized_regular):
                    # Find this number's frequency
                    num_freq = next((f for n, f in freq_list if n == num), 0)
                    if num_freq < least_frequent_val:
                        least_frequent_val = num_freq
                        least_frequent_idx = i
                
                # Replace it with our next best number
                optimized_regular[least_frequent_idx] = next_best_number
            else:
                # If we've exhausted our frequency list, try a random new number
                available_numbers = set(range(1, max_regular + 1)) - set(optimized_regular)
                if available_numbers:
                    # Replace the least frequent number with a random available one
                    least_frequent_idx = 0
                    least_frequent_val = float('inf')
                    
                    for i, num in enumerate(optimized_regular):
                        num_freq = next((f for n, f in freq_list if n == num), 0)
                        if num_freq < least_frequent_val:
                            least_frequent_val = num_freq
                            least_frequent_idx = i
                    
                    # Get the first available number (any would do)
                    new_number = next(iter(available_numbers))
                    optimized_regular[least_frequent_idx] = new_number
        else:
            # We've tried all regular number combinations from frequency list
            # Try generating a random combination that isn't in existing_combinations
            used_numbers = set()
            while len(used_numbers) < 5:
                # Pick the next available frequent number we haven't tried
                for num, _ in freq_list:
                    if num not in used_numbers and len(used_numbers) < 5:
                        used_numbers.add(num)
            
            optimized_regular = sorted(list(used_numbers))
        
        # Sort the regular numbers again
        optimized_regular.sort()
        
        # Recalculate the regular set
        regular_set = tuple(optimized_regular)
        attempts += 1
    
    # Always use the most frequent special ball
    # Return the optimized 5 regular numbers + best special ball
    return optimized_regular + [best_special_ball]

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
    
    # Track draws with missing data
    draws_with_missing_data = 0
    
    # Process each draw
    for draw in draws:
        numbers = draw.get("numbers", [])
        special_ball = draw.get("specialBall")
        
        # Skip draws with missing data
        if len(numbers) != 5 or special_ball is None:
            draws_with_missing_data += 1
            continue
        
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
    
    # If we found draws with missing data, adjust the total
    valid_draws = total_draws - draws_with_missing_data
    if draws_with_missing_data > 0:
        print(f"Warning: Found {draws_with_missing_data} {lottery_type} draws with missing data")
        print(f"Using {valid_draws} valid draws for calculations")
    
    # Validate position frequencies
    print(f"\nValidating frequency counts for {lottery_type}:")
    for pos in range(6):  # 0-4 for regular numbers, 5 for special ball
        pos_str = str(pos)
        pos_freq_sum = sum(frequency_at_position[pos_str].values())
        
        # The sum of frequencies at each position should equal the number of valid draws
        if pos_freq_sum != valid_draws:
            print(f"  Position {pos}: Sum of frequencies ({pos_freq_sum}) != valid draws ({valid_draws})")
            
            # If needed, adjust the frequency counts
            if pos_freq_sum < valid_draws:
                print(f"  Missing {valid_draws - pos_freq_sum} entries at position {pos}")
            else:
                print(f"  Extra {pos_freq_sum - valid_draws} entries at position {pos}")
        else:
            print(f"  Position {pos}: Frequency sum check passed ({pos_freq_sum})")
    
    # Validate that sum of all regular number frequencies equals totalDraws * 5
    total_frequency_sum = sum(frequency.values())
    expected_sum = valid_draws * 5
    if total_frequency_sum != expected_sum:
        print(f"  Total frequency sum ({total_frequency_sum}) != expected sum ({expected_sum})")
        print(f"  Difference: {total_frequency_sum - expected_sum}")
    else:
        print(f"  Total frequency validation: Passed (sum={total_frequency_sum}, expected={expected_sum})")
    
    # Validate that sum of all special ball frequencies equals totalDraws
    special_ball_sum = sum(special_ball_frequency.values())
    if special_ball_sum != valid_draws:
        print(f"  Special ball frequency sum ({special_ball_sum}) != valid draws ({valid_draws})")
        print(f"  Difference: {special_ball_sum - valid_draws}")
    else:
        print(f"  Special ball validation: Passed (sum={special_ball_sum}, expected={valid_draws})")
    
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
    
    # Calculate optimized winning numbers by position that don't exist in previous draws
    optimized_by_position = find_optimized_numbers(position_frequencies, special_freq_list, existing_combinations)
    print(f"Found optimized numbers by position for {lottery_type}: {optimized_by_position}")
    
    # Calculate optimized winning numbers by general frequency that don't exist in previous draws
    optimized_by_general_frequency = find_optimized_numbers_by_general_frequency(
        frequency, special_ball_frequency, existing_combinations, max_regular)
    print(f"Found optimized numbers by general frequency for {lottery_type}: {optimized_by_general_frequency}")
    
    # Sort all frequency dictionaries by frequency (descending)
    sorted_frequency = sort_frequency_dict(frequency)
    sorted_special_ball_frequency = sort_frequency_dict(special_ball_frequency)
    
    # Sort each position's frequency dictionary
    sorted_frequency_at_position = {}
    for pos_str, pos_freq in frequency_at_position.items():
        sorted_frequency_at_position[pos_str] = sort_frequency_dict(pos_freq)
    
    # Create the final statistics object with sorted frequencies
    stats = {
        "type": lottery_type,
        "totalDraws": valid_draws,
        "frequency": sorted_frequency,
        "frequencyAtPosition": sorted_frequency_at_position,
        "specialBallFrequency": sorted_special_ball_frequency,
        "optimizedByPosition": optimized_by_position,
        "optimizedByGeneralFrequency": optimized_by_general_frequency
    }
    
    return stats

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Calculate lottery statistics")
    parser.add_argument("--mm-input", default="data/mm.json", help="Input JSON file with Mega Millions draws")
    parser.add_argument("--pb-input", default="data/pb.json", help="Input JSON file with Powerball draws") 
    parser.add_argument("--mm-output", default="data/mm-stats.json", help="Output file for Mega Millions statistics")
    parser.add_argument("--pb-output", default="data/pb-stats.json", help="Output file for Powerball statistics")
    args = parser.parse_args()
    
    calculate_lottery_stats(args.mm_input, args.pb_input, args.mm_output, args.pb_output)