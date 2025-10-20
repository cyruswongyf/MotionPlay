"""
Train custom gesture recognition model

Before using, install MediaPipe Model Maker:
    pip install mediapipe-model-maker

Usage:
    cd training
    python train_gesture_model.py
"""

from mediapipe_model_maker import gesture_recognizer
import os

# Load data
# Ensure gesture_landmarks.csv path is correct and label column name is correct

data = gesture_recognizer.Dataset.from_csv(
    csv_path='../data/gesture_landmarks.csv',
    delimiter=',',
    label_column='label'
)

# Train model
model = gesture_recognizer.GestureRecognizer.create(
    train_data=data,
    validation_data=None,  # Optional
    epochs=20
)

# Export model to custom_gesture_recognizer folder in project root
model.export_model('../custom_gesture_recognizer')
print('Model exported to custom_gesture_recognizer/gesture_recognizer.task')
