import pandas as pd
import numpy as np

hotel_schema = {
    'hotel_name': str,
    'rate': float,
    'kings': int,
    'doubles': int,
    'triples': int, #triples count as kings
    'five_sixes': int #5-6 count as doubles
}
hotels = pd.read_csv('hotels_robert.txt', delimiter=',', dtype=hotel_schema)
hotels.columns = hotel_schema.keys()

congregation_schema = {
    'congregation_name': str,
    'region': str,
    'total_participants': int,
    'adults': int,
    'kings': int,
    'doubles': int,
    'triples': int,
    'five_sixes': int
}
congregations = pd.read_csv('congregations_robert.txt', delimiter=',', dtype=congregation_schema, encoding='latin-1')
congregations.columns = congregation_schema.keys()
congregation_df = congregations.dropna(how='any')

# Initialize dictionaries to track allocated groups and available room counts
allocated_groups = {}
available_rooms = hotels.set_index('hotel_name').to_dict(orient='index')

# Sort groups in descending order of total room requirements
sorted_groups = congregation_df.sort_values(by=['kings', 
                                                'doubles', 
                                                'triples', 
                                                'five_sixes'], ascending=False)

# Allocate groups to hotels based on requirements and availability
for _, group_row in sorted_groups.iterrows():
    group_name = group_row['congregation_name']
    group_requirements = {
        'kings': group_row['kings'],
        'doubles': group_row['doubles'],
        'triples': group_row['triples'],
        'five_sixes': group_row['five_sixes']
    }

    allocated_hotel = None
    for hotel_name, room_counts in available_rooms.items():
        
        if allocated_hotel is None and all(room_counts[room_type] >= count for room_type, count in group_requirements.items()):
            allocated_hotel = hotel_name
            for room_type, count in group_requirements.items():
                # print(f'taking {count} {room_type} from {hotel_name}')
                available_rooms[hotel_name][room_type] -= count
        else: 
            continue



        if allocated_hotel is not None:
            allocated_groups[group_name] = allocated_hotel
        else: 
            print(f'group {group_name} not given a hotel of {available_rooms}')


# Print the allocated groups
print("Group-Hotel Allocation:")
print(len(allocated_groups))
# for group, hotel in allocated_groups.items():
#     print(f"Group: {group} - Hotel: {hotel}")

# # Print the available rooms for each hotel
print("Available Rooms:")
for hotel, room_counts in available_rooms.items():
    print(f"Hotel: {hotel}")
    for room_type, count in room_counts.items():
        print(f"{room_type}: {count}")