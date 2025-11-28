# MotionPlay

**Gesture-to-Keyboard Controller for Gaming**

Control games with hand gestures using real-time MediaPipe tracking and customizable motion profiles.

## Quick Start

```bash
git clone https://github.com/cyruswongyf/MotionPlay.git && cd MotionPlay
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
python launch.py
```

## Features

• Real-time hand and pose tracking  
• Pre-configured profiles for FPS, Fighting, and Racing games  
• Record and train your own custom gestures  
• Instant motion-to-key mapping with zero lag

## Included Profiles

| Profile      | Game Type            | Core Actions                       |
| ------------ | -------------------- | ---------------------------------- |
| **FPS**      | First-Person Shooter | WASD movement, aim, shoot, reload  |
| **Fighting** | Fighting Games       | Punch, kick, block, special combos |
| **Racing**   | Racing Games         | Steer, accelerate, brake, drift    |

## Add Custom Gestures

Click **Record New Gesture** in the UI, perform the motion 5-10 times, then train with `python train_custom_gesture.py`. Recorded data is saved to `assets/recordings/` and can be shared across installations.
