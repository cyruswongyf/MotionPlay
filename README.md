# MotionPlay

Control your computer with hand gestures and body movements.

## Features

- Real-time hand gesture and pose recognition using MediaPipe
- Record and train your own custom motions
- Map any motion to keyboard or mouse actions

## Quick Start

```bash
git clone https://github.com/cyruswongyf/MotionPlay.git
cd MotionPlay
pip install -r requirements.txt
python launch.py
```

## Usage

1. Launch the application with `python launch.py`
2. Select a profile from the dropdown or create a new one
3. Click "Start Tracking" to begin gesture recognition
4. Perform gestures in front of your camera to trigger mapped actions

## Recording Custom Gestures

1. Open the Motion Library from the main window
2. Click "New Motion" to create a custom gesture
3. Perform the gesture 5-10 times while recording
4. Train the model with `python train_custom_gesture.py`
5. Assign the new gesture to keyboard actions in the Profile Manager

## Configuration

Edit `config.yaml` to customize camera settings, tracking parameters, and UI preferences:

```yaml
camera:
  device_id: 0
  width: 1280
  height: 720
  fps: 30

mediapipe:
  num_hands: 2
  enable_pose: false
  enable_gestures: true

recognition:
  confidence_threshold: 0.7
  cooldown_ms: 500
```

## Project Structure

```
MotionPlay/
├── motionplay/          # Main package
│   ├── core/           # Core functionality (camera, recognition, mapping)
│   ├── ui/             # User interface components
│   ├── styles/         # Theme and styling
│   └── utils/          # Utility functions
├── assets/
│   ├── motions/        # Motion definitions (static and user-created)
│   └── recordings/     # Recorded gesture data
├── models/             # MediaPipe model files
├── profiles/           # Game control profiles
└── config.yaml         # Application configuration
```

## Requirements

- Python 3.8+
- Webcam
- See `requirements.txt` for Python dependencies
