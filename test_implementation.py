#!/usr/bin/env python3
"""
Test script for the multi-method typing identification system.
This script tests all three identification methods: statistical, n-gram, and ML.
"""

import os
import json
import numpy as np
from identify_app.app import (
    load_profiles_statistical, 
    compare_sample_to_profiles_statistical,
    load_profiles_ngram,
    compare_sample_to_profiles_ngram,
    extract_ngram_features,
    train_ml_models,
    predict_ml
)

def test_statistical_method():
    """Test the statistical identification method"""
    print("=== Testing Statistical Method ===")
    
    # Load profiles
    profiles = load_profiles_statistical()
    if not profiles:
        print("❌ No profiles found for statistical method")
        return False
    
    print(f"✅ Found {len(profiles)} user profiles")
    
    # Test with sample data (you can replace this with real data)
    sample_vec = np.array([100.0, 20.0, 50.0, 15.0, 150.0, 25.0])  # Example summary vector
    
    user, acceptance, analysis, matches = compare_sample_to_profiles_statistical(sample_vec, profiles)
    
    print(f"Result: {user}")
    print(f"Acceptance: {acceptance:.3f}")
    print(f"Analysis: {analysis}")
    print(f"Top matches: {[m['user'] for m in matches]}")
    
    return True

def test_ngram_method():
    """Test the n-gram identification method"""
    print("\n=== Testing N-Gram Method ===")
    
    # Load profiles
    profiles = load_profiles_ngram()
    if not profiles:
        print("❌ No profiles found for n-gram method")
        return False
    
    print(f"✅ Found {len(profiles)} user profiles")
    
    # Test with sample data
    sample_data = {
        'text': 'the quick brown fox',
        'ngram_data': {
            'digraphs': {
                'th': [50, 55, 48],
                'he': [45, 50, 47],
                'qu': [60, 65, 58],
                'ui': [40, 42, 38],
                'ck': [55, 60, 52]
            },
            'trigraphs': {
                'the': [120, 125, 118],
                'qui': [100, 105, 98],
                'ick': [110, 115, 108]
            }
        }
    }
    
    sample_features = extract_ngram_features(sample_data)
    if not sample_features:
        print("❌ No n-gram features extracted")
        return False
    
    print(f"✅ Extracted {len(sample_features)} n-gram features")
    
    user, acceptance, analysis, matches = compare_sample_to_profiles_ngram(sample_features, profiles)
    
    print(f"Result: {user}")
    print(f"Acceptance: {acceptance:.3f}")
    print(f"Top matches: {[m['user'] for m in matches]}")
    
    return True

def test_ml_method():
    """Test the machine learning identification method"""
    print("\n=== Testing Machine Learning Method ===")
    
    # Try to train models
    if train_ml_models():
        print("✅ ML models trained successfully")
        
        # Test with sample data
        sample_data = {
            'text': 'the quick brown fox',
            'ngram_data': {
                'digraphs': {
                    'th': [50, 55, 48],
                    'he': [45, 50, 47],
                    'qu': [60, 65, 58],
                    'ui': [40, 42, 38],
                    'ck': [55, 60, 52]
                },
                'trigraphs': {
                    'the': [120, 125, 118],
                    'qui': [100, 105, 98],
                    'ick': [110, 115, 108]
                }
            }
        }
        
        sample_features = extract_ngram_features(sample_data)
        if sample_features:
            user, acceptance, analysis, matches = predict_ml(sample_features)
            print(f"Result: {user}")
            print(f"Acceptance: {acceptance:.3f}")
        else:
            print("❌ No n-gram features for ML prediction")
            return False
    else:
        print("❌ Insufficient data to train ML models")
        return False
    
    return True

def main():
    """Run all tests"""
    print("🧪 Testing Multi-Method Typing Identification System")
    print("=" * 60)
    
    # Check if data directory exists
    data_dir = os.path.join(os.path.dirname(__file__), 'data')
    if not os.path.exists(data_dir):
        print("❌ Data directory not found. Please run the typing game first to collect data.")
        return
    
    # Check if there are any user files
    user_files = [f for f in os.listdir(data_dir) if f.endswith('.json')]
    if not user_files:
        print("❌ No user data found. Please run the typing game first to collect data.")
        return
    
    print(f"✅ Found {len(user_files)} user data files")
    
    # Run tests
    stats_ok = test_statistical_method()
    ngram_ok = test_ngram_method()
    ml_ok = test_ml_method()
    
    print("\n" + "=" * 60)
    print("📊 Test Results Summary:")
    print(f"Statistical Method: {'✅ PASS' if stats_ok else '❌ FAIL'}")
    print(f"N-Gram Method: {'✅ PASS' if ngram_ok else '❌ FAIL'}")
    print(f"ML Method: {'✅ PASS' if ml_ok else '❌ FAIL'}")
    
    if stats_ok and ngram_ok and ml_ok:
        print("\n🎉 All methods are working correctly!")
    else:
        print("\n⚠️  Some methods failed. Check the data and implementation.")

if __name__ == "__main__":
    main() 