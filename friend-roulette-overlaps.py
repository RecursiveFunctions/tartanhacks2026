import csv
from itertools import combinations
from collections import defaultdict

def parse_availability(cell_value):
    """Parse a cell value like 'Sundays, Mondays, Wednesdays' into a set of days"""
    if not cell_value or cell_value.strip() == '':
        return set()
    
    days = [day.strip().rstrip('s') for day in cell_value.split(',')]
    return set(days)

def hour_to_minutes(hour_str):
    """Convert time string like '7am' or '3pm' to minutes since midnight"""
    time_str = hour_str.strip()
    
    # Check if it's am or pm
    if 'am' in time_str:
        hour = int(time_str.replace('am', ''))
        # Handle 12am edge case
        if hour == 12:
            hour = 0
    else:  # pm
        hour = int(time_str.replace('pm', ''))
        if hour != 12:
            hour += 12
    
    return hour * 60

def minutes_to_hour(minutes):
    """Convert minutes since midnight back to 12-hour format"""
    hour = minutes // 60
    if hour == 0:
        return "12am"
    elif hour < 12:
        return f"{hour}am"
    elif hour == 12:
        return "12pm"
    else:
        return f"{hour - 12}pm"

def condense_hour_blocks(hour_blocks):
    """Condense consecutive hour blocks into ranges"""
    if not hour_blocks:
        return []
    
    # Sort hour blocks by start time
    hour_blocks.sort(key=lambda x: hour_to_minutes(x.split(' - ')[0]))
    
    condensed = []
    
    # Parse each block into start and end minutes
    blocks = []
    for block in hour_blocks:
        start_str, end_str = block.split(' - ')
        start_min = hour_to_minutes(start_str)
        end_min = hour_to_minutes(end_str)
        blocks.append((start_min, end_min, block))
    
    # Merge consecutive blocks
    current_start, current_end, _ = blocks[0]
    
    for i in range(1, len(blocks)):
        next_start, next_end, _ = blocks[i]
        
        # If next block starts exactly when current block ends, merge them
        if next_start == current_end:
            current_end = next_end
        else:
            # Add the current merged block
            condensed.append(f"{minutes_to_hour(current_start)} - {minutes_to_hour(current_end)}")
            current_start, current_end = next_start, next_end
    
    # Add the last block
    condensed.append(f"{minutes_to_hour(current_start)} - {minutes_to_hour(current_end)}")
    
    return condensed

def load_availability_data(filename):
    """Load CSV and return dict of {andrew_id: {hour_block: set(days)}}"""
    data = {}
    
    with open(filename, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        
        for row in reader:
            andrew_id = row['AndrewID']
            availability = {}
            
            for col_header in reader.fieldnames:
                if col_header.startswith('Please check which hour blocks'):
                    hour_block = col_header.split('[')[1].split(']')[0]
                    days_available = parse_availability(row[col_header])
                    
                    if days_available:
                        availability[hour_block] = days_available
            
            data[andrew_id] = availability
    
    return data

def find_overlapping_pairs_by_day(availability_data):
    """Find all pairs with overlapping availability, grouped by day with condensed hours"""
    pairs = defaultdict(dict)
    ids = list(availability_data.keys())
    
    for id1, id2 in combinations(ids, 2):
        day_to_hours = defaultdict(list)
        
        # Check each hour block
        for hour_block in set(availability_data[id1].keys()) | set(availability_data[id2].keys()):
            days1 = availability_data[id1].get(hour_block, set())
            days2 = availability_data[id2].get(hour_block, set())
            
            overlapping_days = days1.intersection(days2)
            
            for day in overlapping_days:
                day_to_hours[day].append(hour_block)
        
        if day_to_hours:
            formatted_result = {}
            for day in sorted(day_to_hours.keys()):
                # Condense consecutive hour blocks
                condensed_hours = condense_hour_blocks(day_to_hours[day])
                if condensed_hours:
                    formatted_result[f"{day}s"] = condensed_hours
            
            if formatted_result:
                pairs[(id1, id2)] = formatted_result
    
    return dict(pairs)

def main():
    filename = "CMU Friend Roulette Availability Responses - Form Responses 1.csv"
    
    print("Loading availability data...")
    availability_data = load_availability_data(filename)
    
    print(f"Loaded {len(availability_data)} students:")
    for student_id in availability_data:
        print(f"  {student_id}")
    
    print("\nFinding overlapping pairs (with condensed time ranges)...")
    overlapping_pairs = find_overlapping_pairs_by_day(availability_data)
    
    print(f"\nFound {len(overlapping_pairs)} pairs with overlapping availability:\n")
    print("=" * 60)
    
    # Print results in the elegant format
    for (id1, id2), day_schedule in overlapping_pairs.items():
        print(f"\n{id1} & {id2}:")
        print("-" * 40)
        
        for day, hour_ranges in day_schedule.items():
            hour_str = ", ".join(hour_ranges)
            print(f"  {day}: {hour_str}")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    main()