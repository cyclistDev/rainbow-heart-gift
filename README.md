# RainbowHeart - Improved Version 💕

A romantic animated heart website with hand gesture drawing - created as a gift for your loved one.

## Improvements Made

### 1. ✅ Free Drawing App with Hand Gestures (NEW!)
- **Smart gesture control**: 
  - ✊ **Fist (closed hand)** = STOP drawing
  - ☝️ **One finger up (index finger)** = DRAW
- Draw anything you want with your index finger - letters, words, shapes, hearts
- 10 beautiful colors to choose from
- **On-screen buttons**: Clear and Save buttons on the right sidebar
- Adjustable brush size (press [ ])
- Zoom in/out (press +/-)
- Uses hand gestures - no mouse or touchpad needed!

### 2. ✅ Fixed Text Centering
- Text is now perfectly centered using CSS flexbox and transform
- Responsive font size that scales with screen size
- Improved text positioning on all devices

### 3. ✅ Enhanced Heart Animation
- Added sparkle effects that appear randomly in the background
- Added floating hearts that rise up when you click
- Enhanced color palette with more romantic colors
- Smooth pulsing animation on the main text

### 4. ✅ Interactive Features
- **Click anywhere** to create bursts of hearts and sparkles
- **Particle explosion** - hearts burst in all directions on click
- **Floating "I LOVE YOU" letters** - letters drift across the screen
- **Mouse trail effect** that follows your cursor
- **Romantic background music** with play/pause control
- **Multiple music tracks** - 3 romantic piano tracks with next button
- **Confetti celebration** - click the confetti button for celebration
- **Fullscreen mode** - immersive experience
- **Typewriter effect** - message types out letter by letter
- Click instruction at the bottom of the screen
- Dynamic visual feedback on user interaction

### 5. ✅ Mobile Responsiveness
- Responsive font sizes using CSS clamp()
- Touch-friendly interactions
- Works perfectly on all screen sizes
- Flexible layout that adapts to different devices

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
- Customizable start date (edit line 444 in index.html)

### 8. ✅ Code Improvements
- All CSS embedded in HTML for better portability
- Clean, organized code structure
- Removed unrelated files (about.html, img folder)
- Fixed and improved ani.js with heart animation utilities
- Fixed cmrdraw.py to work with hand gestures (draw with your finger!)

## Files

- **index.html** - Main website with animated hearts and interactive features
- **ani.js** - Additional heart animation utilities (bursts, showers)
- **cmrdraw.py** - Hand gesture drawing app - draw with your index finger!
- **style.css** - Reference file (styles now embedded in HTML)

## How to Use

### Web Version
1. Open `index.html` in any web browser
2. Click the "🎵 Play Music" button to start romantic background music
3. Click anywhere on the screen to create heart bursts and sparkles
4. Move your mouse to see the trail effect
5. Enjoy the animated hearts, pulsing text, and romantic music!

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
   - ✊ **Make a fist** = STOP drawing
   - ☝️ **Raise only index finger** = DRAW
   - 👆 **Point at color buttons** (top) to change colors
   - 👆 **Point at CLR button** (right sidebar) to clear canvas
   - 👆 **Point at SAVE button** (right sidebar) to save drawing
4. **Keyboard Controls**:
   - Press **[ ]** to change brush size
   - Press **+/-** to zoom in/out
   - Press **'q'** to quit
5. **Draw anything you want**:
   - Letters and words
   - Hearts and shapes
   - Doodles and art
   - Anything your heart desires!

## Features

- 🎨 Beautiful rainbow heart animation
- ✨ Sparkle effects throughout
- 💖 Interactive click-to-add hearts
- � Particle explosion on click
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
- 👆 Hand gesture drawing - draw with your finger!

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
