# Recordings Directory

This folder stores recorded gesture sequences for custom motions.

## Structure

Each gesture has its own subdirectory containing multiple JSON files, one per repetition:

```
recordings/
├── punch_forward/
│   ├── recording_1.json
│   └── recording_2.json
└── swipe_left/
    └── recording_1.json
```

MotionPlay automatically detects new gestures in this folder when you launch the application. You can share entire gesture folders with others by copying the subdirectories.

These recordings are used for training custom gesture recognizer models with `train_custom_gesture.py`.
