from flask import Flask, request, render_template, jsonify
from flask_cors import CORS
import os
import json
import numpy as np
from scipy.spatial import distance

app = Flask(__name__)
CORS(app)
DATA_DIR = '../data'

@app.route('/')
def index():
    return render_template('identify.html')

def summary_vector(sample):
    # Returns [mean_hold, std_hold, mean_flight, std_flight, mean_dd, std_dd]
    return np.array([
        np.mean(sample['hold']),
        np.std(sample['hold']),
        np.mean(sample['flight']),
        np.std(sample['flight']),
        np.mean(sample['dd']),
        np.std(sample['dd'])
    ])

def load_profiles():
    profiles = {}
    for fname in os.listdir(DATA_DIR):
        if fname.endswith('.json'):
            with open(os.path.join(DATA_DIR, fname), 'r') as f:
                data = json.load(f)
                summary_vecs = []
                for sample in data.get('samples', []):
                    hold = sample.get('hold_times', [])
                    flight = sample.get('flight_times', [])
                    dd = sample.get('down_down_times', [])
                    if hold and flight and dd:
                        summary_vecs.append(summary_vector({
                            'hold': np.array(hold),
                            'flight': np.array(flight),
                            'dd': np.array(dd)
                        }))
                if summary_vecs:
                    profiles[data['username']] = np.vstack(summary_vecs)
    return profiles

def acceptance_percentage(sample_vec, mean_vec, std_vec, multiplier=2):
    # Returns the percentage of features within mean ± multiplier * std
    within = np.abs(sample_vec - mean_vec) <= multiplier * std_vec
    return np.sum(within) / len(sample_vec)

def compare_sample_to_profiles(sample_vec, profiles, multiplier=2, threshold=0.7):
    best_user = None
    best_accept = 0
    best_analysis = {}
    all_matches = []
    for user, user_mat in profiles.items():
        mean_vec = np.mean(user_mat, axis=0)
        std_vec = np.std(user_mat, axis=0)
        accept = acceptance_percentage(sample_vec, mean_vec, std_vec, multiplier)
        all_matches.append({
            'user': user,
            'acceptance': accept,
            'method': f"Acceptance % within {multiplier} std: {accept*100:.1f}%"
        })
        if accept > best_accept:
            best_accept = accept
            best_user = user
            best_analysis = {
                'avg_hold': float(sample_vec[0]),
                'std_hold': float(sample_vec[1]),
                'avg_flight': float(sample_vec[2]),
                'std_flight': float(sample_vec[3]),
                'avg_dd': float(sample_vec[4]),
                'std_dd': float(sample_vec[5]),
                'acceptance_percentage': accept
            }
    all_matches.sort(key=lambda x: x['acceptance'], reverse=True)
    # Only accept if above threshold
    if best_accept < threshold:
        best_user = 'Unknown User'
    return best_user, best_accept, best_analysis, all_matches[:5]

@app.route('/identify', methods=['POST'])
def identify():
    data = request.get_json()
    hold = data.get('hold_times', [])
    flight = data.get('flight_times', [])
    dd = data.get('down_down_times', [])
    if len(hold) < 5 or len(flight) < 4 or len(dd) < 4:
        return jsonify({'error': 'Insufficient typing data'}), 400
    sample_vec = summary_vector({'hold': np.array(hold), 'flight': np.array(flight), 'dd': np.array(dd)})
    profiles = load_profiles()
    if not profiles:
        return jsonify({'user': 'No profiles found', 'acceptance': 0})
    user, acceptance, analysis, all_matches = compare_sample_to_profiles(sample_vec, profiles)
    return jsonify({
        'user': user,
        'acceptance': float(acceptance),
        'analysis': analysis,
        'all_matches': all_matches
    })

if __name__ == '__main__':
    app.run(port=8001, debug=True) 