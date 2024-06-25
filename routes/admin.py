from flask import Blueprint, request, jsonify
import sqlite3
from transformers import BertTokenizer, BertModel
import torch
from utils.pinecone_utils import PineconeManager

bp = Blueprint('admin', __name__)
tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
model = BertModel.from_pretrained('bert-base-uncased')
pinecone_manager = PineconeManager()

@bp.route('/api/admin/add', methods=['POST'])
def add_property():
    data = request.json
    conn = sqlite3.connect('real_estate.db')
    cursor = conn.cursor()
    cursor.execute('''
    INSERT INTO properties (address, price, bedrooms, bathrooms, parking_spaces, image_url, description)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (data['address'], data['price'], data['bedrooms'], data['bathrooms'], data['parking_spaces'], data['image_url'], data['description']))
    
    property_id = cursor.lastrowid
    description = data['description']
    encoded_input = tokenizer(description, return_tensors="pt", truncation=True, padding=True)
    with torch.no_grad():
        embedding = model(**encoded_input).last_hidden_state[:,0,:].numpy().flatten().tolist()
    
    pinecone_manager.insert(property_id, embedding)

    conn.commit()
    conn.close()
    return jsonify({'message': 'Property added successfully'})

@bp.route('/api/admin/edit/<int:id>', methods=['PUT'])
def edit_property(id):
    data = request.json
    conn = sqlite3.connect('real_estate.db')
    cursor = conn.cursor()
    cursor.execute('''
    UPDATE properties
    SET address=?, price=?, bedrooms=?, bathrooms=?, parking_spaces=?, image_url=?, description=?
    WHERE id=?
    ''', (data['address'], data['price'], data['bedrooms'], data['bathrooms'], data['parking_spaces'], data['image_url'], data['description'], id))
    
    description = data['description']
    encoded_input = tokenizer(description, return_tensors="pt", truncation=True, padding=True)
    with torch.no_grad():
        embedding = model(**encoded_input).last_hidden_state[:,0,:].numpy().flatten().tolist()
    
    pinecone_manager.insert(id, embedding)  # Update the embedding in Pinecone
    
    conn.commit()
    conn.close()
    return jsonify({'message': 'Property updated successfully'})

@bp.route('/api/admin/delete/<int:id>', methods=['DELETE'])
def delete_property(id):
    conn = sqlite3.connect('real_estate.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM properties WHERE id=?', (id,))
    conn.commit()
    conn.close()

    pinecone_manager.delete(id)  # Remove the embedding from Pinecone
    return jsonify({'message': 'Property deleted successfully'})
