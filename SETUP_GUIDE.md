# Setup Guide

## Project Files

### 1. Rainbow Heart Web Display (index.html)
- **Features**: Days counter, photo gallery, romantic music, rainbow heart animation
- **How to use**: Simply open `index.html` in a web browser
- **No installation required**

### 2. FingerCat Webcam App (cat_pet.py)
An index-finger-following webcam pet with a transparent, animated chibi cat sprite.
The cat is loaded from four RGBA PNG frames; MediaPipe tracks the index fingertip,
and the sprite is alpha-composited over the mirrored webcam image.

**Installation:**
```bash
pip install -r requirements-fingercat.txt
```

**Run:**
```bash
python cat_pet.py
```

**Controls:**
- Move your index finger to guide the smoothly-following cat
- Pinch thumb and index finger to make a heart appear
- Click the on-screen **CAT: ON/OFF** button or press `P` to show/hide the cat
- Press `Q` or `Esc` to quit

**Create or replace the sprite frames:**
- Run `python create_cat_frames.py` to generate the included original chibi artwork
  as transparent PNGs in `assets/fingercat/frames/`. The generator uses Pillow.
- To use your own art, put numbered RGBA PNGs (for example, `frame_00.png`,
  `frame_01.png`) in that folder. Keep every frame the same canvas size and save
  with transparency; the app loads them in filename order and loops at 8 FPS.
- Edit the drawing functions in `create_cat_frames.py` to customize the built-in
  cat, or adjust `frames_per_second` when constructing `AnimatedCatSprite` in
  `cat_pet.py` to change animation speed.

### 3. Advanced Hand Gesture Drawing (cmrdraw_advanced.py)
Improved version with all 4 phases implemented:

**Phase 1 - Better Hand Tracking** ✅
- Detects both hands
- Identifies left and right hands consistently
- Tracks 21 landmarks per hand
- Reduces jitter with position smoothing
- Prevents random lines when tracking is lost

**Phase 2 - Smarter Gestures** ✅
- Index finger extended: Draw
- Fist: Stop drawing
- Pinch (thumb + index): Select colors/tools
- Two fingers extended: Additional actions
- Open palm: Pause/Switch modes

**Phase 3 - Advanced Drawing** ✅
- Draw with either hand
- Adjustable brush size (press [ ])
- Eraser mode (press E)
- Undo/Redo (press U/R)
- Smooth lines without lag
- Prevents accidental drawing

**Phase 4 - Performance & Code Quality** ✅
- Improved camera responsiveness
- Separated tracking, gesture recognition, and drawing logic
- Configurable gesture thresholds
- Graceful error handling

**Installation:**
```bash
pip install opencv-python mediapipe==0.10.9 numpy
```

**Run:**
```bash
python cmrdraw_advanced.py
```

**Controls:**
- **Gestures**:
  - Index finger = Draw
  - Fist = Stop
  - Pinch = Select color
  - Open palm = Pause
- **Keyboard**:
  - `[` / `]` = Change brush size
  - `U` = Undo
  - `R` = Redo
  - `C` = Clear canvas
  - `E` = Eraser
  - `S` = Save drawing
  - `Q` = Quit

### 4. Cartoon Cat Pet (cartoon_cat_pet.py)
A cute cartoon cat that follows your hand!

**Features:**
- Cartoon-style cat animation
- Cat follows your hand movement
- Eyes track your hand
- Tail wags
- Cat blinks
- Mood changes (happy, curious, excited)
- Smooth animations

**Installation:**
```bash
pip install opencv-python mediapipe==0.10.9 numpy
```

**Run:**
```bash
python cartoon_cat_pet.py
```

**Controls:**
- Move your hand to attract the cat
- `H` = Happy mood (orange cat)
- `C` = Curious mood (gray cat)
- `E` = Excited mood (pink cat)
- `Q` = Quit

## Customization

### Rainbow Heart Web Display

**Change relationship start date** (line 289 in index.html):
```javascript
const startDate = new Date('2022-10-09'); // Change to your date
```

**Add your photos** (line 508 in index.html):
```javascript
const galleryImages = [
    { src: "your-photo-1.jpg", caption: "Memory 1" },
    { src: "your-photo-2.jpg", caption: "Memory 2" },
    // Add more photos...
];
```

**Change message** (line 411 in index.html):
```html
<h2 class="main-text">
    Your Custom Message Here
</h2>
```

### Advanced Drawing App

**Adjust gesture thresholds** (lines 10-14 in cmrdraw_advanced.py):
```python
class Config:
    PINCH_THRESHOLD = 0.05  # Adjust for pinch sensitivity
    FIST_THRESHOLD = 0.3     # Adjust for fist detection
    OPEN_PALM_THRESHOLD = 0.5
```

**Change camera resolution** (lines 6-7):
```python
    CAMERA_WIDTH = 1280
    CAMERA_HEIGHT = 720
```

### Cartoon Cat Pet

**Adjust cat size** (line 10):
```python
    CAT_SIZE = 150  # Make cat bigger or smaller
```

**Change colors** (lines 64-70 in cartoon_cat_pet.py):
```python
        if self.mood == 'happy':
            body_color = (255, 200, 150)  # Orange
        elif self.mood == 'curious':
            body_color = (200, 200, 200)  # Gray
        else:  # excited
            body_color = (255, 180, 180)  # Pink
```

### 5. Lottie Pet with Hand Tracking (lottie-pet.html) - NEW!
Browser-based pet using your Lottie animation with MediaPipe Hands!

**Features:**
- Uses your Lottie animation from the URL
- Hand tracking with MediaPipe in JavaScript
- Pet follows your hand movement
- Smooth animations
- Pet scales based on hand proximity
- Toggle camera on/off
- Restart the cat animation
- Real-time status display

**How to use:**
- Click **🐱 Lottie Cat** on the main page, or open `lottie-pet.html` in a browser
- For camera tracking, run the project from `http://localhost` or HTTPS (camera access is blocked on many `file://` pages)
- Allow camera access when prompted
- Move your hand to guide the pet
- Pet will follow your hand smoothly
- Click "Toggle Camera" to pause/resume
- Click "Restart Cat" to replay the animation

**No installation required** - runs entirely in browser!

**Customization:**

**Change Lottie animation URL**:
```javascript
const petAnimationUrl = 'https://lottie.host/0b417e38-2cdf-487f-8184-73f3b9499aff/AcGZxUQwpV.json';
```

**Adjust pet size** (line 136):
```javascript
const PET_SIZE = 200;  // Make pet bigger or smaller
```

**Adjust movement smoothness** (line 137):
```javascript
const SMOOTHING_FACTOR = 0.1;  // Lower = smoother but slower
```

**Change hand detection confidence** (lines 310-311):
```javascript
minDetectionConfidence: 0.7,
minTrackingConfidence: 0.5
```

## Troubleshooting

### Camera not working
- Make sure no other app is using the camera
- Try restarting your computer
- Check camera permissions

### Mediapipe errors
- Ensure you have the correct version: `pip install mediapipe==0.10.9`
- If still having issues, try: `pip install --upgrade mediapipe opencv-python`

### Music not playing
- Some browsers block auto-play
- Click the "Play Music" button manually
- Check your internet connection (music is streamed)

### Lottie pet camera not working
- Allow camera access when browser prompts
- Check if another tab is using the camera
- Try refreshing the page
- Ensure HTTPS or localhost (browser security requirement)

## File Structure

```
RainbowHeart-Improved/
├── index.html                    # Rainbow heart web display
├── lottie-pet.html               # Lottie pet with hand tracking (NEW!)
├── cmrdraw_advanced.py           # Advanced hand gesture drawing
├── cartoon_cat_pet.py            # Cartoon cat pet
├── cmrdraw.py                    # Original drawing app (kept for reference)
├── ani.js                        # Animation utilities
├── style.css                     # Reference styles
├── SETUP_GUIDE.md                # This file
└── README.md                     # Main documentation
```

Enjoy your romantic projects! 💕
