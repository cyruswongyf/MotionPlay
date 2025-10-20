# MotionPlay

A real-time gesture recognition application using MediaPipe and OpenCV with custom gesture training capabilities.

## Features

- Real-time pose landmark detection
- Real-time hand gesture recognition
- Custom gesture training
- GUI and CLI modes

## Installation

**Option 1: Using conda**

```bash
conda env create -f environment.yml
conda activate motionplay
python download_models.py
```

**Option 2: Using pip**

```bash
pip install -r requirements.txt
python download_models.py
```

## Usage

**GUI Mode**

```bash
python run_ui.py
```

**CLI Mode**

```bash
python run_cli.py
```

Press **'q'** to quit.

## Training Custom Gestures

1. **Collect gesture data**

   ```bash
   cd training
   python collect_gesture_data.py
   ```

2. **Train the classifier**

   ```bash
   python train_custom_gesture_classifier.py
   ```

3. **Test your gestures**
   ```bash
   cd ../tests
   python test_custom_gesture.py
   ```

The trained model will be saved in `custom_gesture_recognizer/` and automatically used by the application.

## Project Structure

```
MotionPlay/
├── src/                    # Application source code
├── training/               # Training scripts for custom gestures
├── tests/                  # Testing utilities
├── docs/                   # Additional documentation
├── models/                 # MediaPipe model files
├── custom_gesture_recognizer/  # Trained custom models
└── data/                   # Training data
```

## Configuration

- **Confidence Threshold**: Default 70%
- **Gesture Cooldown**: 1 second between repeated gestures
- **Camera Resolution**: 1280x720
- **Target FPS**: 30

## Requirements

- Python 3.8+
- Webcam
- macOS / Linux / Windows

## Credits

- MediaPipe by Google
- OpenCV
- scikit-learn
