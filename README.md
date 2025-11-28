# MotionPlay 🎮✋

**Pro Gaming Gesture Recognition System**

Control your favorite games with hand gestures using computer vision and machine learning. Built with MediaPipe, OpenCV, and PyQt6.

![Version](https://img.shields.io/badge/version-2.0.0-ff1a1a)
![Python](https://img.shields.io/badge/python-3.8+-blue)
![License](https://img.shields.io/badge/license-MIT-green)

---

## 🚀 Features

- **Real-time Hand Gesture Recognition** - Powered by Google MediaPipe
- **Gaming Profiles** - Pre-configured for Fighting Games, FPS, MOBA, Racing, and more
- **Custom Motion Training** - Record and train your own gestures
- **Hot-Reloadable Profiles** - Switch profiles instantly without restart
- **Aggressive Black + Red UI** - Cyberpunk-inspired gaming aesthetic
- **Production-Ready Architecture** - Clean separation of concerns, fully typed, logged

---

## 📋 Requirements

- **Python 3.8+**
- **Webcam** (720p or higher recommended)
- **Operating System**: macOS, Windows, or Linux
- **RAM**: 4GB minimum (8GB recommended)

---

## 🔧 Installation

### 1. Clone the Repository

\`\`\`bash
git clone https://github.com/cyruswongyf/MotionPlay.git
cd MotionPlay
\`\`\`

### 2. Create Virtual Environment (Recommended)

\`\`\`bash

# Using venv

python -m venv venv
source venv/bin/activate # On Windows: venv\\Scripts\\activate

# Or using conda

conda create -n motionplay python=3.10
conda activate motionplay
\`\`\`

### 3. Install Dependencies

\`\`\`bash
pip install -r requirements.txt
\`\`\`

### 4. Download MediaPipe Models

The required MediaPipe models should be in the \`models/\` directory:

- \`hand_landmarker.task\`
- \`pose_landmarker.task\`
- \`gesture_recognizer.task\`

If missing, run the download script:

\`\`\`bash
python download_models.py
\`\`\`

---

## 🎮 Quick Start

### Launch MotionPlay

\`\`\`bash
python main.py
\`\`\`

### First Run

1. **Select a Profile**: Choose from Default, Fighting Game, FPS, MOBA, or Racing
2. **Position Camera**: Ensure your hands are visible in the camera feed
3. **Perform Gestures**: Make gestures like Fist, Open Palm, Victory, etc.
4. **Watch It Work**: See motion names and triggered keys in real-time

---

## 📁 Project Structure

\`\`\`
MotionPlay/
├── core/ # Pure logic (no UI dependencies)
│ ├── camera.py # Camera capture + FPS tracking
│ ├── mediapipe_processor.py # Hand/pose detection + normalization
│ ├── motion_recognizer.py # Motion recognition logic
│ ├── motion_recorder.py # Record gesture sequences
│ └── action_mapper.py # Profile-based key/mouse mapping
│
├── ui/ # PyQt6 GUI components
│ ├── main_window.py # Main application window
│ ├── profile_manager.py # Profile management dialog
│ ├── recording_dialog.py # Motion recording interface
│ └── styles.py # Black + red cyberpunk theme
│
├── profiles/ # YAML profile configurations
│ ├── default.yaml
│ ├── fighting_game.yaml
│ ├── fps.yaml
│ ├── moba.yaml
│ └── racing.yaml
│
├── models/ # MediaPipe .task models
│ ├── hand_landmarker.task
│ ├── pose_landmarker.task
│ └── gesture_recognizer.task
│
├── assets/ # Recordings, icons, etc.
│ └── recordings/ # Saved motion sequences
│
├── config.yaml # Global application settings
├── main.py # Application entry point
├── requirements.txt # Python dependencies
└── README.md # This file
\`\`\`

---

## ⚙️ Configuration

Edit \`config.yaml\` to customize:

\`\`\`yaml

# Camera settings

camera:
device_id: 0 # 0 = default webcam
width: 1280
height: 720
fps: 30
mirror: true

# Recognition thresholds

recognition:
confidence_threshold: 0.7 # 0.0 to 1.0
cooldown_ms: 500 # Time between detections

# Default profile

profiles:
default_profile: default
\`\`\`

---

## 🎯 Creating Custom Profiles

### Profile Structure

Profiles are YAML files in the \`profiles/\` directory:

\`\`\`yaml
name: my_custom_profile

mappings:

# Gesture: Key/Action

Fist: space
Open_Palm: left_click
Victory: w
Thumb_Up: e

# Special keys

Peace: enter
Rock: backspace

# Multiple characters (typed as string)

Shaka: hello
\`\`\`

### Supported Actions

- **Single Characters**: \`a\`, \`b\`, \`1\`, \`2\`, etc.
- **Special Keys**: \`space\`, \`enter\`, \`tab\`, \`backspace\`, \`shift\`, \`ctrl\`, \`alt\`, \`esc\`
- **Arrow Keys**: \`up\`, \`down\`, \`left\`, \`right\`
- **Mouse**: \`left_click\`, \`right_click\`, \`middle_click\`
- **Text Strings**: Any multi-character string gets typed out

### Loading Profiles

1. Place YAML file in \`profiles/\` directory
2. Restart MotionPlay or use **Profile Manager**
3. Select from dropdown or set as active

---

## 🎓 Training Custom Gestures

### Using the Built-in Recorder

1. Click **"RECORD NEW MOTION"** in the main window
2. Enter a motion name (e.g., "Hadouken")
3. Perform the gesture 5 times when countdown finishes
4. Motion is saved to \`assets/recordings/\`

### Training a Custom Model

For advanced users who want to train their own gesture classifier:

\`\`\`bash

# 1. Collect training data

python training/collect_gesture_data.py

# 2. Train the model

python training/train_custom_gesture_classifier.py

# 3. Update config.yaml to use custom classifier

mediapipe:
custom_classifier: custom_gesture_recognizer/gesture_classifier.pkl
\`\`\`

---

## 🎮 Pre-configured Profiles

### Fighting Game Profile

Optimized for Street Fighter, Tekken, Mortal Kombat, etc.

- **Fist**: Light Punch (J)
- **Open Palm**: Heavy Punch (K)
- **Victory**: Light Kick (L)
- **Hadouken**: Fireball (Space)
- **Shoryuken**: Dragon Punch (Shift)

### FPS Profile

Optimized for CS:GO, Valorant, Call of Duty, etc.

- **Fist**: Fire (Left Click)
- **Open Palm**: Aim (Right Click)
- **Victory**: Jump (Space)
- **Thumb Up**: Reload (R)

### MOBA Profile

Optimized for League of Legends, Dota 2, etc.

- **Fist**: Ability Q
- **Open Palm**: Ability W
- **Victory**: Ability E
- **Thumb Up**: Ultimate R

### Racing Profile

Optimized for Forza, Gran Turismo, etc.

- **Thumb Up**: Accelerate (W)
- **Thumb Down**: Brake (S)
- **Pointing Left/Right**: Steer (A/D)
- **Fist**: Handbrake (Space)

---

## 🐛 Troubleshooting

### Camera Not Detected

\`\`\`bash

# List available cameras

python -c "import cv2; print([i for i in range(10) if cv2.VideoCapture(i).isOpened()])"

# Update config.yaml with correct device_id

\`\`\`

### Gestures Not Recognized

1. **Check Lighting**: Ensure good lighting conditions
2. **Adjust Threshold**: Lower \`confidence_threshold\` in \`config.yaml\`
3. **Clear Hand View**: Remove background clutter
4. **Increase Cooldown**: Raise \`cooldown_ms\` if gestures trigger too frequently

### Performance Issues

1. **Lower Resolution**: Reduce camera width/height in config
2. **Reduce FPS**: Lower target FPS in config
3. **Disable Pose**: Set \`enable_pose: false\` if not needed
4. **Close Other Apps**: Free up system resources

### Installation Issues

\`\`\`bash

# If MediaPipe fails to install

pip install --upgrade pip setuptools wheel
pip install mediapipe --no-cache-dir

# If PyQt6 fails

pip install PyQt6 --upgrade
\`\`\`

---

## 📝 Logging

Logs are written to \`logs/motionplay.log\` by default.

View logs in real-time:
\`\`\`bash
tail -f logs/motionplay.log
\`\`\`

Change log level in \`config.yaml\`:
\`\`\`yaml
logging:
level: DEBUG # DEBUG, INFO, WARNING, ERROR, CRITICAL
\`\`\`

---

## 🤝 Contributing

Contributions are welcome! Please follow these guidelines:

1. Fork the repository
2. Create a feature branch (\`git checkout -b feature/amazing-feature\`)
3. Commit your changes (\`git commit -m 'Add amazing feature'\`)
4. Push to the branch (\`git push origin feature/amazing-feature\`)
5. Open a Pull Request

### Code Style

- Follow PEP 8
- Use type hints
- Add docstrings to all functions
- Keep functions pure (no side effects in core modules)

---

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **Google MediaPipe** - Hand and pose detection models
- **OpenCV** - Computer vision library
- **PyQt6** - Modern GUI framework
- **pynput** - Cross-platform input control

---

## 📧 Contact

**Project Maintainer**: Cyrus Wong

- GitHub: [@cyruswongyf](https://github.com/cyruswongyf)
- Project: Final Year Project - HKBU

---

## 🗺️ Roadmap

- [ ] Support for foot gestures (pose-based)
- [ ] Multi-monitor support
- [ ] Cloud profile sync
- [ ] Mobile companion app
- [ ] VR/AR integration
- [ ] Community gesture marketplace

---

## ⭐ Star History

If you find MotionPlay useful, please consider giving it a star! ⭐

---

**Built with ❤️ for gamers who want to level up their control schemes.**

_MotionPlay - Where Motion Meets Action_ 🎮✋🔥
