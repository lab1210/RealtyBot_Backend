from functools import wraps
from flask import Blueprint, request, jsonify
import sqlite3
from transformers import BertTokenizer, BertModel
import torch
import re
from nltk.corpus import stopwords
from utils.pinecone_utils import PineconeManager

bp = Blueprint('recommendations', __name__)

model_ckpt = "bert-base-uncased"
tokenizer = BertTokenizer.from_pretrained(model_ckpt)
model = BertModel.from_pretrained(model_ckpt)

stop_words = stopwords.words('english')

def preprocess_text(text):
    text = text.lower()
    text = re.sub(r'[^\w\s]', '', text)
    tokens = [word for word in text.split() if word not in stop_words]
    return ' '.join(tokens)

def encode_block(sentence):
    encoded_input = tokenizer(sentence, return_tensors="pt", truncation=True, padding=True)
    return encoded_input

pinecone_manager = PineconeManager()

def get_db_connection():
    conn = sqlite3.connect('real_estate.db', check_same_thread=False)
    return conn

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'message': 'Token is missing'}), 403
        # Here you would check the validity of the token
        if token != 'dummy_token':
            return jsonify({'message': 'Invalid token'}), 403
        return f(*args, **kwargs)
    return decorated

@bp.route('/api/recommendations', methods=['POST'])
def get_recommendations():
    user_description = request.json['description']
    preprocessed_user_description = preprocess_text(user_description)
    encoded_input = encode_block(preprocessed_user_description)
    with torch.no_grad():
        user_embedding = model(**encoded_input).last_hidden_state[:,0,:].numpy().flatten().tolist()

    query_results = pinecone_manager.query(user_embedding, top_k=10)

    property_ids = [int(match['id']) for match in query_results['matches']]
    placeholders = ', '.join('?' for _ in property_ids)
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(f'SELECT * FROM properties WHERE id IN ({placeholders})', property_ids)
    recommendations = cursor.fetchall()
    conn.close()

    recommendations_dict = [
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
        for row in recommendations
    ]

    return jsonify(recommendations_dict)
