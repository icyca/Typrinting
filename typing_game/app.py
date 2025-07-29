import os
import json
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, '..', 'data')

if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

@app.route('/')
def serve_typing_game():
    return render_template('typing_game.html')

@app.route('/submit', methods=['POST'])
def submit():
    data = request.get_json()
    username = data.get('username')
    if not username:
        return jsonify({'error': 'No username provided'}), 400
    
    user_file = os.path.join(DATA_DIR, f'{username}.json')
    if os.path.exists(user_file):
        with open(user_file, 'r') as f:
            user_data = json.load(f)
    else:
        user_data = {'username': username, 'samples': []}
    
    # Store all data types for multi-method identification
    sample_data = {
        'text': data.get('text'),
        'hold_times': data.get('hold_times'),
        'flight_times': data.get('flight_times'),
        'down_down_times': data.get('down_down_times'),
        'timings': data.get('timings'),
        'inputHistory': data.get('inputHistory'),
        'errors': data.get('errors'),
        'totalTime': data.get('totalTime'),
        'wpm': data.get('wpm'),
        'accuracy': data.get('accuracy'),
        'difficulty': data.get('difficulty'),
        'timestamp': data.get('timestamp'),
        # New data for enhanced identification methods
        'ngram_data': data.get('ngram_data', {}),
        'keystroke_sequence': data.get('keystroke_sequence', [])
    }
    
    user_data['samples'].append(sample_data)
    
    with open(user_file, 'w') as f:
        json.dump(user_data, f, indent=2)
    
    return jsonify({'status': 'success'})

if __name__ == '__main__':
    app.run(port=8001, debug=True) 