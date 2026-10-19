# RainbowHeart - Improved Version 💕

A romantic animated heart website created as a gift for your loved one.

## Improvements Made

### 1. ✅ Fixed Text Centering
- Text is now perfectly centered using CSS flexbox and transform
- Responsive font size that scales with screen size
- Improved text positioning on all devices

### 2. ✅ Enhanced Heart Animation
- Added sparkle effects that appear randomly in the background
- Added floating hearts that rise up when you click
- Enhanced color palette with more romantic colors
- Smooth pulsing animation on the main text

### 3. ✅ Interactive Features
- **Click anywhere** to create bursts of hearts and sparkles
- **Mouse trail effect** that follows your cursor
- Click instruction at the bottom of the screen
- Dynamic visual feedback on user interaction

### 4. ✅ Mobile Responsiveness
- Responsive font sizes using CSS clamp()
- Touch-friendly interactions
- Works perfectly on all screen sizes
- Flexible layout that adapts to different devices

### 5. ✅ Visual Enhancements
- Beautiful gradient background (dark blue/purple theme)
- Better typography with Georgia serif font
- Enhanced text shadows and glow effects
- More vibrant and romantic color scheme
- Professional-looking animations

### 6. ✅ Code Improvements
- All CSS embedded in HTML for better portability
- Clean, organized code structure
- Removed unrelated files (about.html, img folder)
- Fixed and improved ani.js with heart animation utilities
- Fixed and improved cmrdraw.py (hand gesture heart drawing)

## Files

- **index.html** - Main website with animated hearts and interactive features
- **ani.js** - Additional heart animation utilities (bursts, showers)
- **cmrdraw.py** - Hand gesture heart drawing app using MediaPipe
- **style.css/style.css** - Reference file (styles now embedded in HTML)

## How to Use

### Web Version
1. Open `index.html` in any web browser
2. Click anywhere on the screen to create heart bursts and sparkles
3. Move your mouse to see the trail effect
4. Enjoy the animated hearts and pulsing text!

### Python Heart Drawing App
1. Install dependencies:
   ```bash
   pip install opencv-python mediapipe numpy
   ```
2. Run the script:
   ```bash
   python cmrdraw.py
   ```
3. Use your index finger to draw hearts on the screen
4. Click color buttons at the top to change heart colors
5. Press 'c' to clear the canvas
6. Press 'q' to quit

## Features

- 🎨 Beautiful rainbow heart animation
- ✨ Sparkle effects throughout
- 💖 Interactive click-to-add hearts
- 🖱️ Mouse trail effect
- 📱 Fully responsive design
- 🎁 Perfect romantic gift
- 👆 Hand gesture heart drawing (optional)

## Customization

To customize the message, edit line 206 in index.html:
```html
<h2 class="main-text">
    I Luv You So Much Ouksa!!
</h2>
```

To change colors, modify the `colors` array in the script section of index.html.

Enjoy! 💕
