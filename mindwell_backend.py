from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
from datetime import datetime

app = Flask(__name__)
CORS(app)

# Initialize Database
def init_db():
    with sqlite3.connect('mindwell.db') as conn:
        cursor = conn.cursor()
        # Users Table
        cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                          id INTEGER PRIMARY KEY AUTOINCREMENT,
                          username TEXT UNIQUE NOT NULL,
                          password TEXT NOT NULL)''')
        
        # Mood Tracking Table
        cursor.execute('''CREATE TABLE IF NOT EXISTS mood_entries (
                          id INTEGER PRIMARY KEY AUTOINCREMENT,
                          user_id INTEGER,
                          mood TEXT,
                          note TEXT,
                          timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                          FOREIGN KEY(user_id) REFERENCES users(id))''')
        
        # Peer Support Groups Table
        cursor.execute('''CREATE TABLE IF NOT EXISTS peer_groups (
                          id INTEGER PRIMARY KEY AUTOINCREMENT,
                          name TEXT NOT NULL)''')
        
        # Group Messages Table
        cursor.execute('''CREATE TABLE IF NOT EXISTS group_messages (
                          id INTEGER PRIMARY KEY AUTOINCREMENT,
                          group_id INTEGER,
                          user_id INTEGER,
                          message TEXT NOT NULL,
                          timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                          FOREIGN KEY(group_id) REFERENCES peer_groups(id),
                          FOREIGN KEY(user_id) REFERENCES users(id))''')
        
        conn.commit()

# Route: Home
@app.route('/')
def home():
    return jsonify({'message': 'MindWell API is running!'})

# Route: Register User
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    with sqlite3.connect('mindwell.db') as conn:
        cursor = conn.cursor()
        try:
            cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, password))
            conn.commit()
            return jsonify({'message': 'User registered successfully'}), 201
        except sqlite3.IntegrityError:
            return jsonify({'error': 'Username already exists'}), 400

# Route: Login
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    with sqlite3.connect('mindwell.db') as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT id FROM users WHERE username = ? AND password = ?', (username, password))
        user = cursor.fetchone()
        
        if user:
            return jsonify({'message': 'Login successful', 'user_id': user[0]}), 200
        return jsonify({'error': 'Invalid credentials'}), 401

# Route: Save Mood Entry
@app.route('/mood', methods=['POST'])
def save_mood():
    data = request.get_json()
    user_id = data.get('user_id')
    mood = data.get('mood')
    note = data.get('note')

    with sqlite3.connect('mindwell.db') as conn:
        cursor = conn.cursor()
        cursor.execute('INSERT INTO mood_entries (user_id, mood, note) VALUES (?, ?, ?)', (user_id, mood, note))
        conn.commit()
        return jsonify({'message': 'Mood entry saved successfully'}), 201

# Route: Get Mood Entries
@app.route('/mood/<int:user_id>', methods=['GET'])
def get_moods(user_id):
    with sqlite3.connect('mindwell.db') as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT mood, note, timestamp FROM mood_entries WHERE user_id = ?', (user_id,))
        moods = cursor.fetchall()
        return jsonify({'moods': moods}), 200

# Route: Join Peer Support Group
@app.route('/peer-groups/join', methods=['POST'])
def join_peer_group():
    data = request.get_json()
    group_id = data.get('group_id')
    user_id = data.get('user_id')
    
    with sqlite3.connect('mindwell.db') as conn:
        cursor = conn.cursor()
        cursor.execute('INSERT INTO group_messages (group_id, user_id, message) VALUES (?, ?, ?)', (group_id, user_id, 'User joined the group'))
        conn.commit()
        return jsonify({'message': 'Successfully joined the group'}), 201

# Route: Send Message in Peer Support Group
@app.route('/peer-groups/message', methods=['POST'])
def send_group_message():
    data = request.get_json()
    group_id = data.get('group_id')
    user_id = data.get('user_id')
    message = data.get('message')
    
    with sqlite3.connect('mindwell.db') as conn:
        cursor = conn.cursor()
        cursor.execute('INSERT INTO group_messages (group_id, user_id, message) VALUES (?, ?, ?)', (group_id, user_id, message))
        conn.commit()
        return jsonify({'message': 'Message sent successfully'}), 201

# Route: Get Messages in Peer Group
@app.route('/peer-groups/<int:group_id>/messages', methods=['GET'])
def get_group_messages(group_id):
    with sqlite3.connect('mindwell.db') as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT user_id, message, timestamp FROM group_messages WHERE group_id = ?', (group_id,))
        messages = cursor.fetchall()
        return jsonify({'messages': messages}), 200

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
