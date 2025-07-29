from flask import Flask, request, render_template, jsonify
from flask_cors import CORS
import os
import json
import numpy as np
from scipy.spatial import distance
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import pickle
from werkzeug.datastructures import ContentSecurityPolicy

app = Flask(__name__)
CORS(app)
DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data')
MODELS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'models')

if not os.path.exists(MODELS_DIR):
    os.makedirs(MODELS_DIR)

@app.route('/')
def index():
    return render_template('identify.html')

# ===== STATISTICAL METHOD (Original) =====
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

def load_profiles_statistical():
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

def compare_sample_to_profiles_statistical(sample_vec, profiles, multiplier=2, threshold=0.7):
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

# ===== N-GRAM METHOD =====
def extract_ngram_features(sample):
    """Extract n-gram timing features from a sample"""
    ngram_features = {}
    
    # Extract digraphs and trigraphs from the text
    text = sample.get('text', '').lower()
    digraphs = [text[i:i+2] for i in range(len(text)-1) if text[i:i+2].isalpha()]
    trigraphs = [text[i:i+3] for i in range(len(text)-2) if text[i:i+3].isalpha()]
    
    # Get n-gram data
    ngram_data = sample.get('ngram_data', {})
    digraph_timings = ngram_data.get('digraphs', {})
    trigraph_timings = ngram_data.get('trigraphs', {})
    
    # Calculate features for each n-gram
    for digraph in digraph_timings:
        timings = digraph_timings[digraph]
        if timings:
            ngram_features[f'digraph_{digraph}_mean'] = np.mean(timings)
            ngram_features[f'digraph_{digraph}_std'] = np.std(timings)
    
    for trigraph in trigraph_timings:
        timings = trigraph_timings[trigraph]
        if timings:
            ngram_features[f'trigraph_{trigraph}_mean'] = np.mean(timings)
            ngram_features[f'trigraph_{trigraph}_std'] = np.std(timings)
    
    return ngram_features

def load_profiles_ngram():
    """Load user profiles with n-gram features"""
    profiles = {}
    for fname in os.listdir(DATA_DIR):
        if fname.endswith('.json'):
            with open(os.path.join(DATA_DIR, fname), 'r') as f:
                data = json.load(f)
                user_features = []
                for sample in data.get('samples', []):
                    features = extract_ngram_features(sample)
                    if features:  # Only add if we have n-gram features
                        user_features.append(features)
                if user_features:
                    profiles[data['username']] = user_features
    return profiles

def compare_sample_to_profiles_ngram(sample_features, profiles, threshold=0.6):
    """Compare sample n-gram features to user profiles"""
    best_user = None
    best_score = 0
    all_matches = []
    
    for user, user_features_list in profiles.items():
        if not user_features_list:
            continue
            
        # Calculate similarity for each user sample
        similarities = []
        for user_features in user_features_list:
            # Find common n-grams
            common_keys = set(sample_features.keys()) & set(user_features.keys())
            if not common_keys:
                continue
                
            # Calculate similarity for common n-grams
            total_similarity = 0
            count = 0
            for key in common_keys:
                sample_val = sample_features[key]
                user_val = user_features[key]
                
                # Simple similarity: how close are the values?
                if 'mean' in key:
                    # For means, use relative difference
                    diff = abs(sample_val - user_val) / max(abs(user_val), 1)
                    similarity = max(0, 1 - diff)
                else:
                    # For std, use similar approach
                    diff = abs(sample_val - user_val) / max(abs(user_val), 1)
                    similarity = max(0, 1 - diff)
                
                total_similarity += similarity
                count += 1
            
            if count > 0:
                avg_similarity = total_similarity / count
                similarities.append(avg_similarity)
        
        if similarities:
            user_score = np.mean(similarities)
            all_matches.append({
                'user': user,
                'acceptance': user_score,
                'method': f"N-gram similarity: {user_score*100:.1f}%"
            })
            
            if user_score > best_score:
                best_score = user_score
                best_user = user
    
    all_matches.sort(key=lambda x: x['acceptance'], reverse=True)
    
    if best_score < threshold:
        best_user = 'Unknown User'
    
    return best_user, best_score, {}, all_matches[:5]

# ===== MACHINE LEARNING METHOD =====
def prepare_ml_data():
    """Prepare data for machine learning models"""
    X = []  # Features
    y = []  # Labels
    
    for fname in os.listdir(DATA_DIR):
        if fname.endswith('.json'):
            with open(os.path.join(DATA_DIR, fname), 'r') as f:
                data = json.load(f)
                username = data['username']
                
                for sample in data.get('samples', []):
                    # Extract n-gram features
                    features = extract_ngram_features(sample)
                    if features:
                        # Convert to feature vector
                        feature_vector = []
                        for key in sorted(features.keys()):
                            feature_vector.append(features[key])
                        
                        X.append(feature_vector)
                        y.append(username)
    
    return np.array(X), np.array(y)

def train_ml_models():
    """Train ML models and save them"""
    X, y = prepare_ml_data()
    
    if len(X) < 10:  # Need sufficient data
        return False
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Scale features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # Train KNN
    knn = KNeighborsClassifier(n_neighbors=3)
    knn.fit(X_train_scaled, y_train)
    
    # Train SVM
    svm = SVC(probability=True, random_state=42)
    svm.fit(X_train_scaled, y_train)
    
    # Save models
    with open(os.path.join(MODELS_DIR, 'scaler.pkl'), 'wb') as f:
        pickle.dump(scaler, f)
    with open(os.path.join(MODELS_DIR, 'knn.pkl'), 'wb') as f:
        pickle.dump(knn, f)
    with open(os.path.join(MODELS_DIR, 'svm.pkl'), 'wb') as f:
        pickle.dump(svm, f)
    
    return True

def load_ml_models():
    """Load trained ML models"""
    try:
        with open(os.path.join(MODELS_DIR, 'scaler.pkl'), 'rb') as f:
            scaler = pickle.load(f)
        with open(os.path.join(MODELS_DIR, 'knn.pkl'), 'rb') as f:
            knn = pickle.load(f)
        with open(os.path.join(MODELS_DIR, 'svm.pkl'), 'rb') as f:
            svm = pickle.load(f)
        return scaler, knn, svm
    except:
        return None, None, None

def predict_ml(sample_features):
    """Predict user using ML models"""
    scaler, knn, svm = load_ml_models()
    if scaler is None:
        return 'Unknown User', 0, {}, []
    
    # Prepare feature vector
    feature_vector = []
    for key in sorted(sample_features.keys()):
        feature_vector.append(sample_features[key])
    
    X_sample = np.array([feature_vector])
    X_sample_scaled = scaler.transform(X_sample)
    
    # Get predictions from both models
    knn_pred = knn.predict(X_sample_scaled)[0]
    svm_pred = svm.predict(X_sample_scaled)[0]
    knn_prob = knn.predict_proba(X_sample_scaled)[0]
    svm_prob = svm.predict_proba(X_sample_scaled)[0]
    
    # Use ensemble (majority vote)
    if knn_pred == svm_pred:
        predicted_user = knn_pred
        confidence = (np.max(knn_prob) + np.max(svm_prob)) / 2
    else:
        # If models disagree, use the one with higher confidence
        knn_conf = np.max(knn_prob)
        svm_conf = np.max(svm_prob)
        if knn_conf > svm_conf:
            predicted_user = knn_pred
            confidence = knn_conf
        else:
            predicted_user = svm_pred
            confidence = svm_conf
    
    return predicted_user, confidence, {}, []

# ===== MAIN IDENTIFICATION ENDPOINT =====
@app.route('/identify', methods=['POST'])
def identify():
    data = request.get_json()
    method = data.get('method', 'statistical')
    
    if method == 'statistical':
        # Original statistical method
        hold = data.get('hold_times', [])
        flight = data.get('flight_times', [])
        dd = data.get('down_down_times', [])
        
        if len(hold) < 5 or len(flight) < 4 or len(dd) < 4:
            return jsonify({'error': 'Insufficient typing data'}), 400
        
        sample_vec = summary_vector({
            'hold': np.array(hold), 
            'flight': np.array(flight), 
            'dd': np.array(dd)
        })
        
        profiles = load_profiles_statistical()
        if not profiles:
            return jsonify({'user': 'No profiles found', 'acceptance': 0})
        
        user, acceptance, analysis, all_matches = compare_sample_to_profiles_statistical(sample_vec, profiles)
        
        return jsonify({
            'user': user,
            'acceptance': float(acceptance),
            'analysis': analysis,
            'all_matches': all_matches,
            'method': 'statistical'
        })
    
    elif method == 'ngram':
        # N-gram method
        sample_features = extract_ngram_features(data)
        if not sample_features:
            return jsonify({'error': 'No n-gram features found'}), 400
        
        profiles = load_profiles_ngram()
        if not profiles:
            return jsonify({'user': 'No profiles found', 'acceptance': 0})
        
        user, acceptance, analysis, all_matches = compare_sample_to_profiles_ngram(sample_features, profiles)
        
        return jsonify({
            'user': user,
            'acceptance': float(acceptance),
            'analysis': analysis,
            'all_matches': all_matches,
            'method': 'ngram'
        })
    
    elif method == 'ml':
        # Machine learning method
        sample_features = extract_ngram_features(data)
        if not sample_features:
            return jsonify({'error': 'No n-gram features found'}), 400
        
        # Try to train models if they don't exist
        scaler, knn, svm = load_ml_models()
        if scaler is None:
            if train_ml_models():
                scaler, knn, svm = load_ml_models()
            else:
                return jsonify({'error': 'Insufficient training data for ML models'}), 400
        
        user, acceptance, analysis, all_matches = predict_ml(sample_features)
        
        return jsonify({
            'user': user,
            'acceptance': float(acceptance),
            'analysis': analysis,
            'all_matches': all_matches,
            'method': 'ml'
        })
    
    else:
        return jsonify({'error': 'Invalid method'}), 400

if __name__ == '__main__':
    app.run(port=8001, debug=True) 