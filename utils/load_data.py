import pandas as pd
import sqlite3

def load_property_data(file_path):
    conn = sqlite3.connect('real_estate.db')
    cursor = conn.cursor()

    df = pd.read_excel(file_path)

    for _, row in df.iterrows():
        cursor.execute('''
        INSERT INTO properties (address, price, bedrooms, bathrooms, parking_spaces, image_url, description)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (row['address'], row['price'], row['bedrooms'], row['bathrooms'], row['parking_spaces'], row['image_url'], row['description']))

    conn.commit()
    conn.close()
