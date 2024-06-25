from flask import Blueprint, request, jsonify
from models.user import User
import sqlite3

bp = Blueprint('auth', __name__)

ADMIN_CREDENTIALS = {
    'username': 'admin_username',
    'password': 'admin_password'
}
def get_db_connection():
    conn = sqlite3.connect('real_estate.db', check_same_thread=False)
    return conn

@bp.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data['username']
    password = data['password']
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE username=?', (username,))
    user = cursor.fetchone()
    conn.close()

    is_admin = username == ADMIN_CREDENTIALS['username'] and password == ADMIN_CREDENTIALS['password']

    if user :
         stored_user = User(user[0], user[1], user[2], user[3])
         if stored_user.check_password(password):
            return jsonify({'token': 'dummy_token', 'is_admin': is_admin, 'user_id': stored_user.id}), 200
    elif is_admin:
        return jsonify({'token': 'dummy_token', 'is_admin': True, 'user_id': 'admin'}), 200
    return jsonify({'message': 'Invalid credentials'}), 401

@bp.route('/signup', methods=['POST'])
def signup():
    data = request.json
    username = data['username']
    password = data['password']
    email = data['email']
    user = User(None, username, password, email)
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO users (username, password, email) VALUES (?, ?, ?)',
                   (username, user.password, email))
    conn.commit()
    conn.close()
    return jsonify({'message': 'User created successfully'}), 201

@bp.route('/forgot-password', methods=['POST'])
def forgot_password():
    data = request.json
    email = data['email']
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE email=?', (email,))
    user = cursor.fetchone()
    conn.close()
    
    if user:
        # Here, you would normally send an email with the password reset link
        # For this example, we'll just return a success message
        return jsonify({'message': 'Password reset link sent to your email'}), 200
    return jsonify({'message': 'Email not found'}), 404

@bp.route('/api/user/save_property', methods=['POST'])
def save_property():
    data = request.json
    user_id = data['user_id']
    property_id = data['property_id']
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM saved_properties WHERE user_id=? AND property_id=?', (user_id, property_id))
    existing = cursor.fetchone()
    if existing:
        conn.close()
        return jsonify({'message': 'Property already saved'}), 200
    cursor.execute('''
    INSERT INTO saved_properties (user_id, property_id) VALUES (?, ?)
    ''', (user_id, property_id))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Property saved successfully'}), 201

@bp.route('/api/user/saved_properties', methods=['GET'])
def get_saved_properties():
    user_id = request.args.get('user_id')
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
    SELECT properties.* FROM properties
    JOIN saved_properties ON properties.id = saved_properties.property_id
    WHERE saved_properties.user_id = ?
    ''', (user_id,))
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

@bp.route('/api/user/remove_property', methods=['POST'])
def remove_property():
    data = request.json
    user_id = data['user_id']
    property_id = data['property_id']
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM saved_properties WHERE user_id=? AND property_id=?', (user_id, property_id))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Property removed successfully'}), 200


@bp.route('/api/user/is_saved', methods=['GET'])
def is_saved():
    user_id = request.args.get('user_id')
    property_id = request.args.get('property_id')
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM saved_properties WHERE user_id=? AND property_id=?', (user_id, property_id))
    existing = cursor.fetchone()
    conn.close()
    return jsonify({'is_saved': bool(existing)})

@bp.route('/api/user/profile', methods=['GET'])
def get_user_profile():
    user_id = request.args.get('user_id')
    conn =get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT username, email FROM users WHERE id=?', (user_id,))
    user = cursor.fetchone()

    cursor.execute('SELECT * FROM properties WHERE id IN (SELECT property_id FROM saved_properties WHERE user_id=?)', (user_id,))
    properties = cursor.fetchall()

    conn.close()

    if user is None:
        return jsonify({'message': 'User not found'}), 404

    user_dict = {
        'username': user[0],
        'email': user[1],
        'saved_properties': [
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
    }

    return jsonify(user_dict)
Frontend: User 