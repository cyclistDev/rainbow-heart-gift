# RainbowHeart - Improved Version 💕
### Run the hand-gesture app with `python cmrdraw.py`
A romantic animated heart website with hand gesture drawing - created as a gift for your loved one.

## Improvements Made

### 1. ✅ Free Drawing App with Hand Gestures (NEW!)
- Tracks up to two hands and identifies left and right hands consistently
- Smoothly tracks all 21 MediaPipe landmarks per hand
- ☝️ **Index finger** = draw with either hand; ✊ **Fist** = stop drawing
- 🤏 **Pinch** = select a color or canvas control
- ✌️ **Two fingers** = undo; 🖐️ **Open palm** = pause or resume drawing
- Includes adjustable brushes, an eraser, undo/redo, and canvas controls
- Filters jitter and breaks strokes when a hand is lost or moves abruptly

### 2. ✅ Fixed Text Centering
- Text is now perfectly centered using CSS flexbox and transform
- Responsive font size that scales with screen size
- Improved text positioning on all devices

### 3. ✅ Enhanced Heart Animation
- Added sparkle effects that appear randomly in the background
- Enhanced color palette with more romantic colors
- Smooth pulsing animation on the main text

### 4. ✅ Interactive Features
- **Floating "I LOVE YOU" letters** - letters drift across the screen
- **Mouse trail effect** that follows your cursor
- **Romantic background music** with play/pause control
- **Multiple music tracks** - 3 romantic piano tracks with next button
- **Confetti celebration** - click the confetti button for celebration
- **Fullscreen mode** - immersive experience
- **Typewriter effect** - message types out letter by letter
- Dynamic visual feedback on user interaction
- The click-to-add-hearts and sparkles handler is commented out in `index.html`

### 5. ✅ Mobile Responsiveness
- Responsive font sizes using CSS clamp()
- Touch-friendly interactions
- Works perfectly on all screen sizes
- Flexible layout that adapts to different devices
- The days-together counter stays centered with a simple, uncluttered display
- The gallery stays at the bottom-left, and the Lottie Cat link is an icon
- The Lottie Cat page includes a visible link back to the main page

### 6. ✅ Visual Enhancements
- Beautiful gradient background (dark blue/purple theme)
- Better typography with Georgia serif font
- Enhanced text shadows and glow effects
- More vibrant and romantic color scheme
- Professional-looking animations

### 7. ✅ Romantic Features
- **Days Together Counter** - real-time counter showing how many days you've been together
- Beautiful display at the top of the screen
- Updates every second
- Change the relationship start date by editing the `startDate` value in the script in `index.html`; the date-picker markup and notes are left commented out for later

### 8. ✅ Code Improvements
- All CSS embedded in HTML for better portability
- Clean, organized code structure
- Removed unrelated files (about.html, img folder)
- Fixed and improved ani.js with heart animation utilities
- Separated hand tracking, gesture recognition, and canvas drawing in `cmrdraw.py`

## Files

- **index.html** - Main website with animated hearts and interactive features
- **serve_rainbow_heart.py** - Local web server for camera access and saving captures into the gallery
- **supabase/functions/gallery/index.ts** - Supabase API for public gallery reads and camera uploads
- **supabase/migrations/** - Supabase storage bucket and upload rate-limit setup
- **supabase-config.js** - Public Supabase project URL and anon key used by the GitHub Pages frontend
- **ani.js** - Additional heart animation utilities (bursts, showers)
- **cmrdraw.py** - Two-hand gesture drawing app with adjustable tools and canvas history
- **style.css** - Reference file (styles now embedded in HTML)

## How to Use

### Web Version
1. Run `python serve_rainbow_heart.py` from the project folder and open `http://127.0.0.1:8000`. This local server enables camera access and saves camera captures in the `images` folder. YouTube and the Lottie/hand-tracking libraries also require an internet connection.
2. Click the "🎵 Play Music" button to start romantic background music
3. Click "⏭️ Next Track" to cycle through the playlist, including "Love Shine — Leeheesang"; its YouTube player appears when selected
4. Move your mouse to see the trail effect
5. To change the relationship start date, edit `startDate` in `index.html`
6. Enjoy the animated hearts, pulsing text, and romantic music!

On the Lottie Cat page, select **Start Camera** and allow camera access. The
cat follows the detected index fingertip. The first camera frame is captured
and saved as a JPEG when camera permission is granted, without waiting for a
hand to be detected; saved captures appear in the gallery. The local server
listens only on this computer (`127.0.0.1`). If the hosted Lottie animation
cannot load, a moving cat emoji is shown instead.

The photo gallery displays the images in the `images` folder. Add or replace
static gallery images there and update the `galleryImages` list in `index.html`.

### Deploying camera uploads with GitHub Pages

GitHub Pages cannot run the upload API or permanently save uploaded files in
the repository. The Supabase function and Storage bucket below keep captures
separate from the deployed source files:

1. Create a Supabase project and install the Supabase CLI.
2. Link this repository to the project and deploy the bucket/rate-limit setup:
   ```bash
   supabase login
   supabase link --project-ref YOUR_PROJECT_REF
   supabase db push
   supabase functions deploy gallery
   ```
3. Copy the project URL and a **publishable** (or legacy anon) key into `url`
   and `apiKey` in `supabase-config.js`, then commit and push that public configuration for
   GitHub Pages to serve. These two values are public client configuration;
   never put a Supabase `service_role` key in this file or in GitHub Pages.
4. In GitHub repository settings, enable Pages for the branch/folder containing
   the HTML files and wait for deployment. The camera requires the HTTPS Pages
   URL (or localhost during local testing).

When a visitor starts the camera and grants permission, the first camera frame
is automatically uploaded to the **public** `camera-captures` gallery. The page
discloses this before camera use and shows an on-screen alert only when an
index finger is detected. The API accepts JPEGs up to 5 MB and limits
uploads to five per IP-address hash per hour. Anyone can view uploaded images,
so do not use public uploads if captures should be private. If enabling
`verify_jwt` for the function, keep it disabled as configured: the function
validates a public publishable/anon key itself and uses the server-side secret
key for storage access.

Uploaded images do **not** appear in GitHub or this repository's `images/`
folder. In Supabase, open **Storage → camera-captures** to view the objects.
The bucket is created by `supabase db push`; captures are uploaded there by the
Edge Function. The function URL is checked before camera permission is
requested, so a missing config file, undeployed function, or unavailable bucket
is reported before the camera starts.

### Python Drawing App - Hand Gesture Control
1. Install dependencies:
   ```bash
   pip install opencv-python mediapipe==0.10.9 numpy
   ```
2. Run the script:
   ```bash
   python cmrdraw.py
   ```
3. **Gesture Controls**:
   - ☝️ **Raise only your index finger** = draw with either hand
   - ✊ **Make a fist** = stop drawing
   - 🤏 **Pinch thumb and index finger** over the top palette or a right-side button to select it; follow the yellow cursor ring and wait for the on-screen confirmation
   - ✌️ **Raise index and middle fingers** = undo
   - 🖐️ **Open your palm** = pause or resume drawing
   - Pinch the right-side **CLEAR**, **UNDO**, **REDO**, **BRUSH -/+**, **ERASER**, **ZOOM -/+**, **PAUSE**, or **SAVE** buttons
   - All drawing controls are available in the webcam view; the keyboard is optional
4. **Optional Keyboard Shortcuts**:
   - Press **[ ]** to decrease/increase brush size
   - Press **E** to toggle the eraser
   - Press **Ctrl+Z / Ctrl+Y** to undo/redo
   - Press **P** to pause/resume
   - Press **+/-** to zoom the webcam view in/out (0.5x to 3.0x)
   - Press **S** to save the drawing
   - Press **Q** to quit
5. **Draw anything you want**:
   - Letters and words
   - Hearts and shapes
   - Doodles and art
   - Anything your heart desires!

The drawing is saved as `love_drawing.png` in the same folder as `cmrdraw.py`.
Pinch the on-screen **SAVE** button or press **S**; a success or failure message
appears in the webcam window, and the full save path is printed in the terminal.
This saves the drawing canvas (with its black background), not a webcam photograph.
Tracking confidence, smoothing, and gesture stability thresholds are configurable
near the top of `cmrdraw.py`.

### FingerCat Webcam Pet

Run `python cat_pet.py` for the MediaPipe webcam pet. It tracks the index fingertip,
smoothly follows it, and overlays an animated chibi cat made from transparent PNG
sprite frames. The drawing app in `cmrdraw.py` and the RainbowHeart web app are
separate and remain unchanged.

Install dependencies with `pip install -r requirements-fingercat.txt`. The included
four-frame sprite is in `assets/fingercat/frames/`; run `python create_cat_frames.py`
to regenerate it. To use your own art, replace those with same-sized transparent
RGBA PNGs named in frame order (such as `frame_00.png`, `frame_01.png`). The loader
composites the frames over the webcam feed and loops at 8 FPS.

## Features

- 🎨 Beautiful rainbow heart animation
- ✨ Sparkle effects throughout
- 🔤 Floating "I LOVE YOU" letters
- �🖱️ Mouse trail effect
- 🎵 Romantic background music (3-track playlist)
- 🎉 Confetti celebration button
- 🖥️ Fullscreen mode
- 📷 Screenshot button
- ⌨️ Typewriter text effect
- 💕 Days together counter
- 📱 Fully responsive design
- 🎁 Perfect romantic gift
- 👆 Two-hand gesture drawing with undo/redo and eraser!

## Customization

To customize the message, edit line 179 in index.html:
```html
<h2 class="main-text">
    I Love You So Much, Babe Ouksa!!
</h2>
```

To change colors, modify the `colors` array in the script section of index.html.

To change the background music, edit the audio source in line 186:
```html
<audio id="bgMusic" loop>
    <source src="YOUR_MUSIC_URL_HERE" type="audio/mpeg">
</audio>
```

Music source: Romantic Piano from Pixabay (royalty-free, no attribution required)

Enjoy! 💕
