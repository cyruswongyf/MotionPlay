#!/usr/bin/env python3
"""
Custom Gesture Training Script for MotionPlay
Trains custom gesture recognizer from recorded data.
"""

import os
import sys
import json
import argparse
import logging
from pathlib import Path
from typing import List, Dict, Any
import numpy as np

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def load_recordings(data_dir: Path) -> Dict[str, List[Any]]:
    """Load all gesture recordings from directory structure."""
    logger.info(f"Loading recordings from {data_dir}")
    
    gesture_data = {}
    
    if not data_dir.exists():
        logger.error(f"Data directory not found: {data_dir}")
        return gesture_data
    
    # Iterate through gesture folders
    for gesture_dir in data_dir.iterdir():
        if not gesture_dir.is_dir() or gesture_dir.name.startswith('.'):
            continue
        
        gesture_name = gesture_dir.name
        gesture_sequences = []
        
        # Load all JSON files in this gesture folder
        for json_file in gesture_dir.glob('*.json'):
            try:
                with open(json_file, 'r') as f:
                    data = json.load(f)
                    
                # Extract sequences
                if 'sequences' in data:
                    for sequence in data['sequences']:
                        gesture_sequences.append({
                            'gesture_name': gesture_name,
                            'sequence': sequence,
                            'source_file': str(json_file)
                        })
                
                logger.info(f"Loaded {len(data.get('sequences', []))} sequences from {json_file.name}")
                
            except Exception as e:
                logger.error(f"Failed to load {json_file}: {e}")
        
        if gesture_sequences:
            gesture_data[gesture_name] = gesture_sequences
            logger.info(f"Gesture '{gesture_name}': {len(gesture_sequences)} total sequences")
    
    return gesture_data


def prepare_mediapipe_data(gesture_data: Dict[str, List[Any]]) -> tuple:
    """Prepare data in MediaPipe Model Maker format."""
    logger.info("Preparing data for MediaPipe Model Maker")
    
    all_landmarks = []
    all_labels = []
    
    for gesture_name, sequences in gesture_data.items():
        for seq_data in sequences:
            sequence = seq_data['sequence']
            
            # Extract landmark coordinates from sequence
            # Shape: [num_frames, num_landmarks * 3] (x, y, z for each landmark)
            sequence_landmarks = []
            
            for frame in sequence:
                if 'hands' in frame and len(frame['hands']) > 0:
                    # Use first hand (or you can modify to handle multiple hands)
                    hand = frame['hands'][0]
                    landmarks = hand['landmarks']
                    
                    # Flatten landmarks: [x1, y1, z1, x2, y2, z2, ...]
                    flat_landmarks = []
                    for lm in landmarks:
                        flat_landmarks.extend([lm[0], lm[1], lm[2]])
                    
                    sequence_landmarks.append(flat_landmarks)
            
            if sequence_landmarks:
                all_landmarks.append(np.array(sequence_landmarks, dtype=np.float32))
                all_labels.append(gesture_name)
    
    logger.info(f"Prepared {len(all_landmarks)} sequences across {len(set(all_labels))} gestures")
    return all_landmarks, all_labels


def train_with_tensorflow(gesture_data: Dict[str, List[Any]], output_path: Path, epochs: int = 30):
    """Train custom gesture model using TensorFlow/Keras."""
    try:
        import tensorflow as tf
        from tensorflow import keras
        from sklearn.model_selection import train_test_split
        from sklearn.preprocessing import LabelEncoder
    except ImportError:
        logger.error("TensorFlow not installed. Install with: pip install tensorflow scikit-learn")
        return False
    
    logger.info("Training with TensorFlow/Keras")
    
    # Prepare data
    X, y = prepare_mediapipe_data(gesture_data)
    
    if not X:
        logger.error("No valid training data")
        return False
    
    # Encode labels
    label_encoder = LabelEncoder()
    y_encoded = label_encoder.fit_transform(y)
    num_classes = len(label_encoder.classes_)
    
    logger.info(f"Gesture classes: {list(label_encoder.classes_)}")
    
    # Pad sequences to same length
    max_length = max(len(seq) for seq in X)
    X_padded = tf.keras.preprocessing.sequence.pad_sequences(
        X, maxlen=max_length, dtype='float32', padding='post'
    )
    
    # Split into train/validation
    X_train, X_val, y_train, y_val = train_test_split(
        X_padded, y_encoded, test_size=0.2, random_state=42, stratify=y_encoded
    )
    
    logger.info(f"Training set: {len(X_train)} samples")
    logger.info(f"Validation set: {len(X_val)} samples")
    
    # Build LSTM model
    model = keras.Sequential([
        keras.layers.LSTM(128, return_sequences=True, input_shape=(max_length, X_padded.shape[2])),
        keras.layers.Dropout(0.3),
        keras.layers.LSTM(64),
        keras.layers.Dropout(0.3),
        keras.layers.Dense(64, activation='relu'),
        keras.layers.Dropout(0.2),
        keras.layers.Dense(num_classes, activation='softmax')
    ])
    
    model.compile(
        optimizer='adam',
        loss='sparse_categorical_crossentropy',
        metrics=['accuracy']
    )
    
    logger.info("Model architecture:")
    model.summary()
    
    # Train
    logger.info(f"Training for {epochs} epochs...")
    
    history = model.fit(
        X_train, y_train,
        validation_data=(X_val, y_val),
        epochs=epochs,
        batch_size=32,
        callbacks=[
            keras.callbacks.EarlyStopping(
                monitor='val_loss',
                patience=5,
                restore_best_weights=True
            ),
            keras.callbacks.ReduceLROnPlateau(
                monitor='val_loss',
                factor=0.5,
                patience=3
            )
        ]
    )
    
    # Evaluate
    logger.info("\n" + "="*60)
    logger.info("Training Complete!")
    logger.info("="*60)
    
    train_loss, train_acc = model.evaluate(X_train, y_train, verbose=0)
    val_loss, val_acc = model.evaluate(X_val, y_val, verbose=0)
    
    logger.info(f"Training Accuracy: {train_acc*100:.2f}%")
    logger.info(f"Validation Accuracy: {val_acc*100:.2f}%")
    
    # Save model
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Save as SavedModel format
    saved_model_dir = output_path.parent / f"{output_path.stem}_savedmodel"
    model.save(saved_model_dir)
    logger.info(f"Model saved to: {saved_model_dir}")
    
    # Save label encoder
    label_file = output_path.parent / f"{output_path.stem}_labels.json"
    with open(label_file, 'w') as f:
        json.dump({
            'classes': label_encoder.classes_.tolist(),
            'num_classes': num_classes
        }, f, indent=2)
    logger.info(f"Labels saved to: {label_file}")
    
    # Confusion matrix
    try:
        from sklearn.metrics import confusion_matrix, classification_report
        
        y_pred = np.argmax(model.predict(X_val, verbose=0), axis=1)
        cm = confusion_matrix(y_val, y_pred)
        
        logger.info("\nConfusion Matrix:")
        logger.info(str(cm))
        
        logger.info("\nClassification Report:")
        logger.info(classification_report(
            y_val, y_pred,
            target_names=label_encoder.classes_
        ))
    except Exception as e:
        logger.warning(f"Could not generate detailed metrics: {e}")
    
    logger.info("\n" + "="*60)
    logger.info("Note: This model is in TensorFlow format.")
    logger.info("To use in MotionPlay, you'll need to integrate TensorFlow inference.")
    logger.info("For MediaPipe .task format, install mediapipe-model-maker.")
    logger.info("="*60)
    
    return True


def main():
    """Main training script."""
    parser = argparse.ArgumentParser(
        description='Train custom gesture recognizer for MotionPlay',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python train_custom_gesture.py
  python train_custom_gesture.py --data assets/recordings --epochs 50
  python train_custom_gesture.py --output models/my_custom_gestures.task
        """
    )
    
    parser.add_argument(
        '--data',
        type=str,
        default='assets/recordings',
        help='Directory containing gesture recordings (default: assets/recordings)'
    )
    parser.add_argument(
        '--output',
        type=str,
        default='models/custom_gesture_recognizer',
        help='Output path for trained model (default: models/custom_gesture_recognizer)'
    )
    parser.add_argument(
        '--epochs',
        type=int,
        default=30,
        help='Number of training epochs (default: 30)'
    )
    parser.add_argument(
        '--method',
        type=str,
        choices=['tensorflow', 'mediapipe'],
        default='tensorflow',
        help='Training method (default: tensorflow)'
    )
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("MotionPlay Custom Gesture Trainer")
    print("=" * 60)
    print()
    
    # Load recordings
    data_dir = Path(args.data)
    gesture_data = load_recordings(data_dir)
    
    if not gesture_data:
        logger.error("No gesture data found!")
        logger.info("\nMake sure you have recordings in this structure:")
        logger.info("  assets/recordings/")
        logger.info("    gesture_name_1/")
        logger.info("      *.json")
        logger.info("    gesture_name_2/")
        logger.info("      *.json")
        return 1
    
    # Summary
    print()
    print("=" * 60)
    print("Training Data Summary")
    print("=" * 60)
    total_sequences = sum(len(seqs) for seqs in gesture_data.values())
    print(f"Total Gestures: {len(gesture_data)}")
    print(f"Total Sequences: {total_sequences}")
    print()
    for gesture_name, sequences in gesture_data.items():
        print(f"  • {gesture_name}: {len(sequences)} sequences")
    print("=" * 60)
    print()
    
    # Validate minimum data
    if total_sequences < 10:
        logger.warning("⚠️  Warning: Less than 10 total sequences. More data recommended!")
    
    for gesture_name, sequences in gesture_data.items():
        if len(sequences) < 3:
            logger.warning(f"⚠️  Warning: '{gesture_name}' has only {len(sequences)} sequences. 5+ recommended!")
    
    # Train model
    output_path = Path(args.output)
    
    if args.method == 'tensorflow':
        success = train_with_tensorflow(gesture_data, output_path, epochs=args.epochs)
    else:
        logger.error("MediaPipe Model Maker training not yet implemented.")
        logger.info("Use --method tensorflow for now.")
        success = False
    
    if success:
        print()
        print("=" * 60)
        print("✅ Training Complete!")
        print("=" * 60)
        return 0
    else:
        print()
        print("=" * 60)
        print("❌ Training Failed")
        print("=" * 60)
        return 1


if __name__ == '__main__':
    sys.exit(main())
