import pandas as pd
import numpy as np

#set print params
pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)

#set globals
MAX_CAPACITY=0.9

PRICE_RANGE_MAPPING = {
    'A': '$140-150 + tax',
    'B': '$151-165 + tax',
    'C': '$166-185 + tax',
}

LOCATION_MAPPING = {
    '1': 'French Quarter',
    '2': 'Superdome',
    '3': 'Downtown',
    '4': 'Convention Center'
}

hotels_raw = pd.read_csv('hotels.csv', delimiter=',')
hotels = hotels_raw[['Hotel', 'Code', 'Requested Kings with teams', 'Requested KP with teams', 'Requested Double with teams', 'Requested DP with teams']]

hotels.columns = hotels.columns \
        .str.strip() \
        .str.replace(r" ", '_', regex=True) \
        .str.lower()

hotels['kings'] = np.round((hotels['requested_kings_with_teams'] + hotels['requested_kp_with_teams']) * MAX_CAPACITY).astype(int)
hotels['doubles'] = np.round((hotels['requested_double_with_teams'] + hotels['requested_dp_with_teams']) * MAX_CAPACITY).astype(int)
hotels['initial_kings'] = hotels['kings']
hotels['initial_doubles'] = hotels['doubles']
hotels['price_range'] = hotels['code'].str[3:].map(PRICE_RANGE_MAPPING)
hotels['location'] = hotels['code'].str[0].map(LOCATION_MAPPING)

#TODO: put a general file name
congregations_raw = pd.read_csv('housing_report.csv', delimiter=',')
congregations = congregations_raw[['Cong ID', 'Congregation Name', 'Kings Requested', 'Doubles Requested', 'Priority Incentive', 'Hotel Price Range', 'Hotel Location']]

congregations.columns = congregations.columns \
    .str.strip()\
    .str.replace(r" ", '_', regex=True) \
    .str.lower()

congregations[['kings_requested', 'doubles_requested']] = congregations[['kings_requested', 'doubles_requested']].fillna(0).astype(int)
congregations['priority_incentive'] = congregations['priority_incentive'].str.upper()

# Initialize dictionaries to track allocated groups and available room counts
allocated_groups = {}
available_rooms = hotels.set_index('hotel').to_dict(orient='index')

# Sort groups in descending order of total room requirements
sorted_groups = congregations\
    # .sort_values(by=['doubles_requested', 
    #                  'kings_requested'], 
    #              ascending=False)

# Allocate groups to hotels based on requirements and availability
for _, group_row in sorted_groups.iterrows():

    if (group_row['kings_requested'] == 0 and group_row['doubles_requested'] == 0):
        continue #skip groups that didn't supply proper values

    group_name = group_row['congregation_name']
    group_id = group_row['cong_id']
    room_requirements = {
        'kings': group_row['kings_requested'],
        'doubles': group_row['doubles_requested']
    }
    preference = group_row['priority_incentive']

    #Initialize the hotel to nothing
    allocated_hotel = None
    for hotel_name, hotel_data in available_rooms.items():

        #Check preference
        if preference == 'HOTEL PRICE':
            if group_row['hotel_price_range'] != hotel_data['price_range']: 
                # print(f'skipping {hotel_name} for group {group_name}')
                continue #skip the hotel if not in the right price range
        elif preference == 'HOTEL LOCATION':
            if group_row['hotel_location'] != hotel_data['location']:
                # print(f'skipping {hotel_name} for group {group_name}')
                continue #skip the hotel if not in the right location
        else: 
            pass #do nothing if a group didn't include a location/price preference
        
        if all(hotel_data[room_type] >= count for room_type, count in room_requirements.items()):
            allocated_hotel = hotel_name

            #Decrement the room count
            for room_type, count in room_requirements.items():
                available_rooms[hotel_name][room_type] -= count

            allocated_groups[group_id] = allocated_hotel
            break #break the inner loop and continue to the next group
    if allocated_hotel is None: 
        print(f"group {group_name} not given a hotel. Group details: {room_requirements},  Group preference: {preference}, Group price pref: {group_row['hotel_price_range']}")

hotel_report = pd.DataFrame(available_rooms)
hotel_report.T.to_csv('hotels_post_algo.csv')

congregations['assigned_hotel'] = congregations['cong_id'].map(allocated_groups)
congregations.sort_values(by=['priority_incentive', 'hotel_price_range', 'hotel_location', 'assigned_hotel']).reset_index(drop=True).to_csv('congregations_post_algo.csv')