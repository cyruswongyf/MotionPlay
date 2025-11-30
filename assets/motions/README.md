# MotionPlay Motion Library

Professional gesture recognition motion database for MotionPlay v2.

## Directory Structure

```
assets/motions/
├── static/          # Built-in motions (shipped with MotionPlay)
│   ├── hadoken/
│   │   ├── preview.gif
│   │   ├── metadata.json
│   │   └── samples/
│   └── ...
└── user/            # Custom user-trained motions
    ├── punch_forward/
    │   ├── preview.gif
    │   ├── metadata.json
    │   └── samples/
    └── ...
```

## Motion Folder Contents

Each motion folder must contain:

1. **metadata.json** - Motion metadata (required)

   ```json
   {
     "motion_id": "static/hadoken",
     "display_name": "Hadoken",
     "description": "Classic fireball projectile motion",
     "category": "special_move",
     "difficulty": "medium",
     "tags": ["projectile", "fireball"],
     "preview_gif": "preview.gif",
     "author": "MotionPlay Team",
     "created_date": "2026-01-01",
     "version": "1.0"
   }
   ```

2. **preview.gif** - Animated preview thumbnail (recommended 200x200px)

3. **samples/** - Training sample recordings (optional)

## Categories

- `basic_attack` - Basic punches, kicks, blocks
- `special_move` - Special moves, combos, signature attacks
- `movement` - Dash, dodge, jump motions
- `gesture` - General gestures and commands

## Adding Custom Motions

1. Create new folder in `assets/motions/user/your_motion_name/`
2. Add `metadata.json` with motion details
3. Add `preview.gif` (or placeholder image)
4. Record training samples in `samples/` folder
5. Motion will appear in Motion Library dialog under "My Motions" tab

## Motion ID Format

- Built-in: `static/motion_name`
- Custom: `user/motion_name`

Motion IDs are used in profile YAML mappings.
