"""
Train custom gesture classifier using collected landmarks data

This script uses sklearn to train a simple but effective gesture classification model
No need for mediapipe-model-maker, avoids TensorFlow version issues

Install required packages:
    pip install scikit-learn pandas numpy joblib

Usage:
    cd scripts
    python train_custom_gesture_classifier.py
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
import joblib
import os

# Configuration paths
CSV_PATH = '../data/gesture_landmarks.csv'
MODEL_OUTPUT_PATH = '../custom_gesture_recognizer/gesture_classifier.pkl'

def load_and_prepare_data(csv_path):
    """Load and prepare training data"""
    print(f"Loading data from: {csv_path}")
    df = pd.read_csv(csv_path)
    
    # Separate features and labels
    X = df.drop('label', axis=1)
    y = df['label']
    
    print(f"Total samples: {len(df)}")
    print(f"Number of features: {X.shape[1]}")
    print(f"Gesture classes: {y.unique()}")
    print(f"Class distribution:\n{y.value_counts()}")
    
    return X, y

def train_model(X, y):
    """Train Random Forest classifier"""
    # Split into training and test sets
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    print(f"\nTraining set size: {len(X_train)}")
    print(f"Test set size: {len(X_test)}")
    
    # Train model
    print("\nStarting model training...")
    model = RandomForestClassifier(
        n_estimators=100,
        max_depth=20,
        random_state=42,
        n_jobs=-1
    )
    
    model.fit(X_train, y_train)
    
    # Evaluate model
    print("\nModel training completed!")
    train_score = model.score(X_train, y_train)
    test_score = model.score(X_test, y_test)
    
    print(f"Training accuracy: {train_score:.4f}")
    print(f"Test accuracy: {test_score:.4f}")
    
    # Detailed evaluation
    y_pred = model.predict(X_test)
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred))
    
    print("\nConfusion Matrix:")
    print(confusion_matrix(y_test, y_pred))
    
    return model

def save_model(model, output_path):
    """Save trained model"""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    joblib.dump(model, output_path)
    print(f"\nModel saved to: {output_path}")

def main():
    # Check if data file exists
    if not os.path.exists(CSV_PATH):
        print(f"Error: Data file not found at {CSV_PATH}")
        print("Please collect gesture data using collect_gesture_data.py first")
        return
    
    # Load data
    X, y = load_and_prepare_data(CSV_PATH)
    
    # Train model
    model = train_model(X, y)
    
    # Save model
    save_model(model, MODEL_OUTPUT_PATH)
    
    print("\n✅ Complete! You can now use this model for gesture recognition")
    print(f"Model file: {MODEL_OUTPUT_PATH}")

if __name__ == "__main__":
    main()
