# Typrinting - Multi-Method Typing Identification System

A comprehensive typing biometrics system that identifies users based on their typing patterns using three different methods: statistical analysis, n-gram analysis, and machine learning.

## 🚀 Features

### Three Identification Methods

1. **Statistical Method (Original)**
   - Uses mean and standard deviation of hold, flight, and down-down times
   - Best for same text identification
   - Fast and simple

2. **N-Gram Analysis**
   - Analyzes timing patterns between character pairs (digraphs) and triplets (trigraphs)
   - Works well with different texts
   - More robust than statistical method for cross-text identification

3. **Machine Learning**
   - Uses scikit-learn (KNN and SVM) on n-gram features
   - Most accurate but requires more training data
   - Automatically trains models when sufficient data is available

### Data Collection
- **Comprehensive Data Gathering**: Collects all data types simultaneously during typing
- **N-Gram Extraction**: Automatically extracts digraph and trigraph timing patterns
- **Keystroke Sequences**: Records detailed keystroke sequences for analysis

## 📁 Project Structure

```
Typrinting/
├── data/                    # User profile data
│   ├── bob.json
│   └── Espana.json
├── typing_game/            # Data collection app
│   ├── app.py
│   ├── static/
│   │   └── typing_game.js  # Enhanced with n-gram collection
│   └── templates/
│       └── typing_game.html
├── identify_app/           # Identification app
│   ├── app.py             # Multi-method identification backend
│   ├── models/            # Trained ML models
│   ├── static/
│   │   ├── identify.js    # Enhanced with method selection
│   │   └── identify.css
│   └── templates/
│       └── identify.html  # Method selection UI
├── TODO.md                # Implementation roadmap
├── test_implementation.py # Test script
└── README.md
```

## 🛠️ Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd Typrinting
   ```

2. **Install dependencies**
   ```bash
   # For typing game
   cd typing_game
   pip install -r requirements.txt
   
   # For identification app
   cd ../identify_app
   pip install -r requirements.txt
   ```

## 🎮 Usage

### 1. Data Collection (Typing Game)

```bash
cd typing_game
python app.py
```

- Open `http://localhost:8001`
- Enter your username
- Type the prompts to build your profile
- **All data types are collected automatically** (statistical, n-gram, ML-ready)

### 2. User Identification

```bash
cd identify_app
python app.py
```

- Open `http://localhost:8001`
- Select your preferred identification method:
  - **Statistical**: Best for same text
  - **N-Gram**: Good for different texts
  - **Machine Learning**: Most accurate (requires sufficient data)
- Type the prompt and get identified

## 🔬 How It Works

### Statistical Method
- Extracts 6 features: `[mean_hold, std_hold, mean_flight, std_flight, mean_dd, std_dd]`
- Compares test sample to user profiles using acceptance percentage
- Threshold-based decision making

### N-Gram Method
- Extracts digraphs (2-grams) and trigraphs (3-grams) from text
- Calculates timing features for each n-gram: `mean` and `std`
- Compares overlapping n-grams between test and profiles
- More robust for different texts

### Machine Learning Method
- Uses n-gram features as input to ML models
- Trains KNN and SVM classifiers
- Ensemble prediction with confidence scores
- Requires at least 10 samples across users

## 📊 Method Comparison

| Method | Same Text | Different Text | Accuracy | Speed | Data Requirements |
|--------|-----------|----------------|----------|-------|-------------------|
| Statistical | ✅ Excellent | ❌ Poor | Medium | Fast | Low |
| N-Gram | ✅ Good | ✅ Good | High | Medium | Medium |
| ML | ✅ Excellent | ✅ Excellent | Very High | Slow | High |

## 🧪 Testing

Run the test script to verify all methods work:

```bash
python test_implementation.py
```

This will test:
- Statistical method with sample data
- N-gram feature extraction
- ML model training and prediction
- All three identification methods

## 🔧 Configuration

### Thresholds
- **Statistical**: Default 0.7 (70% acceptance)
- **N-Gram**: Default 0.6 (60% similarity)
- **ML**: Automatic confidence-based

### N-Gram Settings
- **Digraphs**: 2-character sequences (e.g., "th", "he")
- **Trigraphs**: 3-character sequences (e.g., "the", "qui")
- **Alphabetic only**: Filters out non-letter characters

## 🚀 Future Enhancements

- [ ] Real-time identification during typing
- [ ] Adaptive thresholds per user
- [ ] More ML algorithms (Random Forest, Neural Networks)
- [ ] Cross-platform compatibility
- [ ] API endpoints for integration
- [ ] Performance optimization for large datasets

## 📝 Technical Notes

### Data Format
Each user profile contains:
```json
{
  "username": "user",
  "samples": [
    {
      "text": "prompt text",
      "hold_times": [...],
      "flight_times": [...],
      "down_down_times": [...],
      "ngram_data": {
        "digraphs": {"th": [...], "he": [...]},
        "trigraphs": {"the": [...], "qui": [...]}
      },
      "keystroke_sequence": [...]
    }
  ]
}
```

### ML Models
- **KNN**: k=3 neighbors
- **SVM**: RBF kernel with probability estimates
- **Ensemble**: Majority vote with confidence weighting
- **Persistence**: Models saved in `identify_app/models/`

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Implement your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is open source and available under the MIT License. 
