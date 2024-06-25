from flask import Blueprint, request, jsonify
import sqlite3

bp = Blueprint('properties', __name__)

def get_db_connection():
    conn = sqlite3.connect('real_estate.db', check_same_thread=False)
    return conn

@bp.route('/api/properties', methods=['GET'])
def get_properties():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM properties')
    properties = cursor.fetchall()
    conn.close()

    properties_dict = [
        {
            'id': row[0],
            'address': row[1],
            'price': row[2],
            'bedrooms': row[3],
            'bathrooms': row[4],
            'parking_spaces': row[5],
            'image_url': row[6],
            'description': row[7]
        }
        for row in properties
    ]

    return jsonify(properties_dict)

@bp.route('/api/properties/<int:id>', methods=['GET'])
def get_property(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM properties WHERE id=?', (id,))
    property = cursor.fetchone()
    conn.close()

    if property is None:
        return jsonify({'message': 'Property not found'}), 404

    property_dict = {
        'id': property[0],
        'address': property[1],
        'price': property[2],
        'bedrooms': property[3],
        'bathrooms': property[4],
        'parking_spaces': property[5],
        'image_url': property[6],
        'description': property[7]
    }

    return jsonify(property_dict)
