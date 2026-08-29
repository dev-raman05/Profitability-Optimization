import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings('ignore')

print("Reading data...")
fact = pd.read_csv('Given dataset/fact_bookings.csv', parse_dates=['booking_date', 'check_in_date', 'checkout_date'], dayfirst=True)
fact_agg = pd.read_csv('Given dataset/fact_aggregated_bookings.csv', parse_dates=['check_in_date'])
room = pd.read_csv('Given dataset/dim_rooms.csv').rename(columns={'room_id': 'room_category'})
hotel = pd.read_csv('Given dataset/dim_hotels.csv')
date_hot = pd.read_csv('Given dataset/dim_date.csv', parse_dates=['date']).rename(columns={'date': 'check_in_date'})

print("Merging...")
df = fact.merge(fact_agg, on=['property_id', 'check_in_date', 'room_category'], how='left')
df = df.merge(hotel, on='property_id', how='left')
df = df.merge(date_hot, on='check_in_date', how='left')
df = df.merge(room, on='room_category', how='left')

print("Feature Engineering...")
df['length_of_stay'] = (df['checkout_date'] - df['check_in_date']).dt.days
df['advance_booking'] = (df['check_in_date'] - df['booking_date']).dt.days
df['Profitability_Index'] = df['revenue_realized'] / df['revenue_generated']

print("Imputing ratings (no data leakage)...")
# Imputing using median rating of the property and room category
df['ratings_given'] = df.groupby(['property_id', 'room_category'])['ratings_given'].transform(lambda x: x.fillna(x.median()))
# If still any NaNs, fill with overall median
df['ratings_given'] = df['ratings_given'].fillna(df['ratings_given'].median())

print("Saving...")
df.drop(columns=['booking_id', 'room_category', 'booking_date', 'checkout_date'], inplace=True, errors='ignore')

# Arrange columns
cols = ['check_in_date', 'property_id', 'property_name', 'category', 'city', 'room_class', 'no_guests', 
        'booking_platform', 'booking_status', 'ratings_given', 'revenue_generated', 'revenue_realized', 
        'Profitability_Index', 'successful_bookings', 'capacity', 'mmm yy', 'week no', 
        'day_type', 'length_of_stay', 'advance_booking']
df = df[cols]

df.to_csv("big_data_file.csv", index=False)
df.to_parquet("big_data_file.parquet", index=False)
print("Done!")
