from flask import Flask
from flask_cors import CORS
from routes import auth, properties, recommendations, admin
import sqlite3
from utils.load_data import load_property_data
import warnings
warnings.filterwarnings("ignore")

app = Flask(__name__)
CORS(app)

def create_tables():
    conn = sqlite3.connect('real_estate.db')
    cursor = conn.cursor()
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        username TEXT UNIQUE,
        password TEXT,
        email TEXT UNIQUE
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS properties (
        id INTEGER PRIMARY KEY,
        address TEXT,
        price TEXT,
        bedrooms INTEGER,
        bathrooms INTEGER,
        parking_spaces INTEGER,
        image_url TEXT,
        description TEXT
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS saved_properties (
        user_id INTEGER,
        property_id INTEGER,
        PRIMARY KEY (property_id),
        FOREIGN KEY (user_id) REFERENCES users(id),
        FOREIGN KEY (property_id) REFERENCES properties(id)
    )
    ''')
    
    conn.commit()
    conn.close()


# Create tables if they don't exist
create_tables()

# Load initial property data from Excel
load_property_data('data/properties.xlsx')

# Register blueprints
app.register_blueprint(auth.bp)
app.register_blueprint(properties.bp)
app.register_blueprint(recommendations.bp)
app.register_blueprint(admin.bp)

if __name__ == '__main__':
    app.run(debug=True)
