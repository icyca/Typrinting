# TODO: Multi-Method Typing Identification System

## Phase 1: Data Collection Enhancement
- [ ] Modify typing_game to collect all data types simultaneously
  - [ ] Regular timing data (hold, flight, down-down)
  - [ ] N-gram timing data (digraphs, trigraphs)
  - [ ] Raw keystroke sequences for ML
- [ ] Update data storage format to support multiple data types
- [ ] Ensure typing_game collects data regardless of method (all methods get all data)

## Phase 2: N-Gram Feature Implementation
- [ ] Create n-gram extraction functions
  - [ ] Extract digraphs (2-grams): "th", "he", "qu", etc.
  - [ ] Extract trigraphs (3-grams): "the", "qui", "bro", etc.
  - [ ] Calculate timing features for each n-gram
- [ ] Implement n-gram profile building
  - [ ] Store mean/std for each n-gram per user
  - [ ] Handle n-grams that appear in some samples but not others
- [ ] Implement n-gram matching algorithm
  - [ ] Compare only overlapping n-grams between test and profile
  - [ ] Aggregate similarity scores across all matching n-grams

## Phase 3: Machine Learning Implementation
- [ ] Implement scikit-learn based identification
  - [ ] KNN classifier for n-gram features
  - [ ] SVM classifier as alternative
  - [ ] Feature preprocessing and normalization
- [ ] Train/test split and model evaluation
- [ ] Model persistence (save/load trained models)

## Phase 4: UI Enhancement
- [ ] Add method selection dropdown to identify_app
  - [ ] "Statistical" (current method)
  - [ ] "N-Gram" (new n-gram method)
  - [ ] "Machine Learning" (ML method)
- [ ] Update frontend to send selected method to backend
- [ ] Display method-specific results and confidence scores

## Phase 5: Backend Method Routing
- [ ] Modify identify endpoint to handle different methods
- [ ] Implement method-specific identification logic
- [ ] Ensure backward compatibility with existing data
- [ ] Add method validation and error handling

## Phase 6: Testing and Validation
- [ ] Test with same text (should work well)
- [ ] Test with different text (n-gram/ML should work better)
- [ ] Compare accuracy across methods
- [ ] Performance testing with larger datasets

## Phase 7: Documentation and Cleanup
- [ ] Update README with new methods
- [ ] Add code comments explaining each method
- [ ] Create usage examples
- [ ] Performance optimization if needed

## Technical Notes
- N-gram method will be more robust for different texts
- ML method will require more training data but should be most accurate
- Statistical method remains as baseline for comparison
- All methods will use the same data collection process 