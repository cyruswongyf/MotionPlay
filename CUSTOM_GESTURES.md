# Custom Gesture Training Guide

## 🎯 Overview

MotionPlay supports training custom gestures for game-specific actions. This guide explains how to record, train, and use custom gestures.

---

## 📁 Directory Structure

```
assets/recordings/
├── Hadouken/                       # Custom gesture 1
│   ├── Hadouken_seq1_20231128_120000.json
│   ├── Hadouken_seq2_20231128_120005.json
│   ├── Hadouken_seq3_20231128_120010.json
│   ├── Hadouken_seq4_20231128_120015.json
│   └── Hadouken_seq5_20231128_120020.json
├── Shoryuken/                      # Custom gesture 2
│   ├── Shoryuken_seq1_20231128_120100.json
│   └── ...
└── Kamehameha/                     # Custom gesture 3
    └── ...
```

Each gesture should have **5+ sequences** for good training results.

---

## 🎬 Recording Custom Gestures

### Step 1: Launch Recording Dialog

In MotionPlay main window, click **"RECORD NEW MOTION"**.

### Step 2: Enter Gesture Name

Enter a descriptive name (e.g., "Hadouken", "Kamehameha", "ShieldBlock").

**Naming Tips:**

- Use alphanumeric characters only
- No spaces (use underscores: `Fire_Spell`)
- Be descriptive and consistent

### Step 3: Record Sequences

1. **Countdown**: 3...2...1...
2. **Record**: Perform gesture (3 seconds)
3. **Repeat**: 5 times automatically

**Recording Tips:**

- Perform gesture clearly and consistently
- Use same hand (left/right) for all sequences
- Maintain good lighting
- Keep hands in camera view
- Exaggerate movements slightly
- Repeat the same motion pattern

### Step 4: Review Saved Data

Recordings are saved to `assets/recordings/[gesture_name]/`.

Each file contains:

- **60 frames** (resampled automatically)
- **Normalized landmarks** (relative to wrist)
- **Metadata** (timestamp, confidence scores)

---

## 📊 Data Format

### JSON Structure

```json
{
  "gesture_name": "Hadouken",
  "num_sequences": 1,
  "target_frames": 60,
  "normalized": true,
  "sequences": [
    [
      {
        "timestamp": "2023-11-28T12:00:00.123456",
        "hands": [
          {
            "handedness": "Right",
            "landmarks": [
              [0.0, 0.0, 0.0], // Wrist (normalized to origin)
              [0.1, 0.05, 0.02], // Thumb CMC
              [0.15, 0.08, 0.03] // Thumb MCP
              // ... 21 landmarks total
            ],
            "score": 0.95
          }
        ]
      }
      // ... 60 frames total
    ]
  ],
  "metadata": {
    "recorded_at": "2023-11-28T12:00:20.000000",
    "num_landmarks_per_hand": 21,
    "format_version": "1.0"
  }
}
```

### Landmark Indices

MediaPipe Hand Landmarks (21 points):

```
0:  Wrist
1:  Thumb_CMC
2:  Thumb_MCP
3:  Thumb_IP
4:  Thumb_TIP
5:  Index_MCP
6:  Index_PIP
7:  Index_DIP
8:  Index_TIP
9:  Middle_MCP
10: Middle_PIP
11: Middle_DIP
12: Middle_TIP
13: Ring_MCP
14: Ring_PIP
15: Ring_DIP
16: Ring_TIP
17: Pinky_MCP
18: Pinky_PIP
19: Pinky_DIP
20: Pinky_TIP
```

---

## 🚀 Training Custom Model

### Prerequisites

```bash
pip install tensorflow scikit-learn
```

### Training Command

```bash
# Basic training
python train_custom_gesture.py

# Custom options
python train_custom_gesture.py \
    --data assets/recordings \
    --output models/custom_gesture_recognizer \
    --epochs 50
```

### Training Process

1. **Load Recordings**: Scans `assets/recordings/` for gesture folders
2. **Prepare Data**:
   - Extracts landmark sequences
   - Encodes labels
   - Splits train/validation (80/20)
3. **Build Model**: LSTM architecture with dropout
4. **Train**: With early stopping and learning rate reduction
5. **Evaluate**: Reports accuracy and confusion matrix
6. **Save**: Exports model to `models/`

### Expected Output

```
==================================================
Training Data Summary
==================================================
Total Gestures: 3
Total Sequences: 15

  • Hadouken: 5 sequences
  • Shoryuken: 5 sequences
  • Kamehameha: 5 sequences
==================================================

Training for 30 epochs...

Epoch 30/30
12/12 [======] - 0s 5ms/step - loss: 0.0523 - accuracy: 0.9833

==================================================
Training Complete!
==================================================
Training Accuracy: 99.17%
Validation Accuracy: 95.83%

Confusion Matrix:
[[5 0 0]
 [0 5 0]
 [0 1 4]]

Model saved to: models/custom_gesture_recognizer_savedmodel
```

---

## 🎮 Using Custom Gestures

### Auto-Detection

MotionPlay automatically detects and loads custom models:

1. Train model → saved to `models/custom_gesture_recognizer.task`
2. Restart MotionPlay
3. Custom gestures available immediately!

**Console Output:**

```
INFO - Custom gesture recognizer detected: models/custom_gesture_recognizer.task
INFO - Loaded custom gestures: Hadouken, Shoryuken, Kamehameha
```

### Manual Selection

Edit `config.yaml`:

```yaml
mediapipe:
  gesture_model: models/custom_gesture_recognizer.task
```

### Adding to Profiles

Edit your game profile (e.g., `profiles/fighting_game.yaml`):

```yaml
name: fighting_game

mappings:
  # Built-in gestures
  Fist: j
  Open_Palm: k

  # Custom gestures
  Hadouken: space
  Shoryuken: shift
  Kamehameha: ctrl
```

---

## 💡 Best Practices

### Recording Quality

✅ **Do:**

- Record in good lighting
- Use consistent hand (left/right)
- Perform gesture smoothly
- Record 5+ sequences per gesture
- Exaggerate movements slightly
- Keep hands in frame

❌ **Don't:**

- Switch hands mid-recording
- Record in poor lighting
- Rush through gestures
- Record with cluttered background
- Use ambiguous gestures

### Training Tips

1. **More Data = Better Accuracy**

   - Minimum: 5 sequences per gesture
   - Recommended: 10+ sequences
   - Ideal: 20+ sequences

2. **Diverse Examples**

   - Record at different speeds
   - Slight variations in hand position
   - Different lighting conditions

3. **Clear Distinctions**

   - Make gestures visually distinct
   - Avoid similar hand shapes
   - Use different motion patterns

4. **Regular Retraining**
   - Add new sequences periodically
   - Retrain to improve accuracy
   - Test in real gaming scenarios

---

## 🐛 Troubleshooting

### Low Accuracy

**Problem:** Model accuracy below 80%

**Solutions:**

- Record more sequences (10+ per gesture)
- Ensure gestures are distinct
- Check lighting consistency
- Remove ambiguous recordings
- Increase training epochs: `--epochs 50`

### Gestures Not Detected

**Problem:** Custom gestures not recognized in-game

**Solutions:**

- Verify model file exists: `models/custom_gesture_recognizer.task`
- Check console logs for errors
- Restart MotionPlay
- Lower confidence threshold in `config.yaml`

### Recording Issues

**Problem:** Recording fails or saves empty files

**Solutions:**

- Ensure camera is working
- Check hands are visible
- Verify `assets/recordings/` directory exists
- Check disk space

---

## 📈 Advanced: Model Metrics

### Confusion Matrix

Shows which gestures are confused with each other:

```
                Predicted
              H   S   K
Actual    H  [5   0   0]
          S  [0   5   0]
          K  [0   1   4]
```

**Interpretation:**

- Diagonal = Correct predictions
- Off-diagonal = Confusion between classes
- Example: 1 Kamehameha mistaken for Shoryuken

### Classification Report

```
              precision  recall  f1-score  support
Hadouken         1.00     1.00     1.00      5
Shoryuken        0.83     1.00     0.91      5
Kamehameha       1.00     0.80     0.89      5

accuracy                          0.93     15
```

**Key Metrics:**

- **Precision**: % of predictions that were correct
- **Recall**: % of actual gestures detected
- **F1-Score**: Harmonic mean of precision/recall

---

## 🎯 Example Use Cases

### Fighting Game

Record 3 special moves:

- Hadouken (fireball)
- Shoryuken (uppercut)
- Spinning Bird Kick

### MOBA/RPG

Record ability gestures:

- Fire Spell (both hands up)
- Ice Shield (crossing arms)
- Lightning Strike (one hand forward)

### Racing Game

Record hand signals:

- Start Engine (fist pump)
- Drift (hand wave)
- Boost (double fist)

---

## 📝 Quick Reference

| Task             | Command                                      |
| ---------------- | -------------------------------------------- |
| Record gesture   | Click "RECORD NEW MOTION" in UI              |
| Train model      | `python train_custom_gesture.py`             |
| Custom epochs    | `python train_custom_gesture.py --epochs 50` |
| Check recordings | `ls assets/recordings/`                      |
| Verify model     | `ls models/custom_gesture_recognizer*`       |

---

**Next:** [Creating Game Profiles](profiles/README.md) • [Troubleshooting](TROUBLESHOOTING.md)
