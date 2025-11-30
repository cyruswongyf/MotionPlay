# MotionPlay v3.1

**Professional Air Gesture Recognition for Gaming**

Control games with hand gestures using real-time MediaPipe tracking and customizable motion profiles.

---

## 🚀 Quick Start

```bash
git clone https://github.com/cyruswongyf/MotionPlay.git
cd MotionPlay
python -m venv venv && source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
python launch.py
```

---

## ✨ Features

• **Real-time Tracking** - Hand and pose tracking powered by MediaPipe  
• **Pre-built Profiles** - Ready-made profiles for FPS, Fighting, MOBA, and Racing games  
• **Custom Gestures** - Record and train your own gestures with the built-in trainer  
• **Zero Lag** - Direct keyboard input with professional debouncing  
• **Hot Reload** - Edit profiles while the app is running  
• **Open Source** - Clean, maintainable, well-documented code

---

## 📦 Project Structure (v3.1)

```
MotionPlay/
├── motionplay/                 # Main package (new organized structure)
│   ├── core/                   # Core functionality
│   │   ├── camera.py          # Camera capture and management
│   │   ├── mediapipe_processor.py  # MediaPipe integration
│   │   ├── motion_recognizer.py    # Gesture recognition logic
│   │   ├── action_mapper.py   # Motion-to-keyboard mapping
│   │   └── motion_recorder.py # Recording system
│   ├── models/                 # Model management
│   │   └── model_manager.py   # Auto-download MediaPipe models
│   ├── ui/                     # User interface
│   │   ├── main_window.py     # Main application window
│   │   ├── dialogs/           # Dialog windows
│   │   │   ├── recording_dialog.py
│   │   │   ├── motion_edit_dialog.py
│   │   │   ├── motion_library_dialog.py
│   │   │   └── profile_manager.py
│   │   └── widgets/           # Reusable UI components
│   │       ├── mapping_table.py
│   │       ├── profile_list.py
│   │       └── key_selector_dialog.py
│   ├── styles/                 # Centralized styling
│   │   ├── colors.py          # Color palette definitions
│   │   ├── themes.py          # Theme application
│   │   └── stylesheets.py     # Component stylesheets
│   └── utils/                  # Utilities
│       ├── dark_dialogs.py    # Dark-themed dialog helpers
│       └── base_ui.py         # Base UI classes
├── assets/                     # Asset files
│   ├── motions/               # Motion definitions
│   │   ├── static/            # Built-in motions
│   │   └── user/              # User-created motions
│   └── recordings/            # Recorded gesture data
├── models/                     # MediaPipe model files (.task)
├── profiles/                   # Game control profiles (.yaml)
├── config.yaml                 # Application configuration
├── main.py                     # Application entry point
├── launch.py                   # Quick launcher with checks
└── train_custom_gesture.py    # Custom gesture trainer
```

---

## 🎮 Included Profiles

| Profile      | Game Type            | Core Actions                       |
| ------------ | -------------------- | ---------------------------------- |
| **FPS**      | First-Person Shooter | WASD movement, aim, shoot, reload  |
| **Fighting** | Fighting Games       | Punch, kick, block, special combos |
| **MOBA**     | MOBA Games          | QWER abilities, items, ping        |
| **Racing**   | Racing Games         | Steer, accelerate, brake, drift    |

---

## 🛠️ Adding Custom Gestures

1. **Record**: Click "Motion Library" → "New Motion" in the UI
2. **Perform**: Execute the gesture 5-10 times clearly
3. **Train**: Run `python train_custom_gesture.py`
4. **Use**: Assign to keys in Profile Manager

Recorded data is saved to `assets/recordings/` and can be shared across installations.

---

## 🎨 Architecture Highlights (v3.1)

### Clean Separation of Concerns
- **Core**: Pure logic, no UI dependencies
- **UI**: Clean interfaces using signals/slots
- **Styles**: Centralized colors and themes
- **Utils**: Reusable helpers and dialogs

### Unified Theme System
```python
from motionplay.styles import apply_dark_theme

app = QApplication(sys.argv)
apply_dark_theme(app)  # Single call - consistent everywhere
```

### Professional Package Structure
- All imports use absolute paths from `motionplay.*`
- No circular dependencies
- Easy to test and extend
- IDE-friendly with full autocomplete

---

## 📝 Configuration

Edit `config.yaml` to customize:

```yaml
camera:
  device_id: 0        # Camera index
  width: 1280
  height: 720
  fps: 30
  mirror: true        # Mirror video feed

mediapipe:
  num_hands: 2        # Track up to 2 hands
  enable_pose: false  # Enable full-body tracking
  enable_gestures: true

recognition:
  confidence_threshold: 0.7  # Minimum confidence
  cooldown_ms: 500          # Debounce time
  debounce_time: 0.8        # Action debounce

ui:
  window_width: 1400
  window_height: 820
  overlay:
    show_landmarks: true        # Show hand landmarks
    trigger_feedback: true      # Show trigger overlays
```

---

## 🔧 Development

### Running from Source
```bash
python main.py              # Direct run
python main.py --offline    # Skip model downloads
```

### Package Installation (Coming Soon)
```bash
pip install motionplay
```

### Testing
```bash
pytest tests/              # Run test suite
python -m motionplay.core.camera  # Test camera
```

---

## 📚 API Usage

```python
from motionplay import (
    Camera, MediaPipeProcessor, 
    MotionRecognizer, ActionMapper
)

# Initialize components
camera = Camera(camera_id=0, width=1280, height=720)
processor = MediaPipeProcessor(num_hands=2)
recognizer = MotionRecognizer(confidence_threshold=0.7)
mapper = ActionMapper(profile_dir='profiles', initial_profile='fps')

# Processing loop
while True:
    ret, frame = camera.read_frame()
    processor.process_frame(frame, timestamp_ms)
    gestures = processor.get_gestures()
    detection = recognizer.recognize_from_gestures(gestures, timestamp_ms)
    
    if detection:
        action = mapper.get_action(detection['motion'])
        if mapper.trigger_action(detection['motion']):
            print(f"Triggered: {detection['motion']} → {action}")
```

---

## 🤝 Contributing

We welcome contributions! This v3.1 restructure makes the codebase:

- **Easy to Navigate**: Logical file organization
- **Easy to Extend**: Clear interfaces and separation
- **Easy to Test**: Modular, testable components
- **Easy to Document**: Self-explanatory structure

See `CONTRIBUTING.md` for guidelines.

---

## 📄 License

MIT License - See `LICENSE` file for details

---

## 🌟 Acknowledgments

- **MediaPipe** - Google's ML framework for hand/pose tracking
- **PyQt6** - Professional Python GUI framework
- **pynput** - Keyboard/mouse control library

---

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/cyruswongyf/MotionPlay/issues)
- **Discussions**: [GitHub Discussions](https://github.com/cyruswongyf/MotionPlay/discussions)
- **Email**: cyrus.wong@motionplay.dev

---

**MotionPlay v3.1** - Built with ❤️ for the gaming community
