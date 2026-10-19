// Heart Animation Functions
// This file contains additional animation utilities for the heart effects

const heartColors = ["#e03776","#8f3e98","#4687bf","#3bab6f","#f9c25e","#f47274","#ff6b9d","#c44569","#ff8a5c","#ff3c83"];

// Create a burst of hearts at position
function createHeartBurst(x, y, count = 10) {
    for (let i = 0; i < count; i++) {
        setTimeout(() => {
            const angle = (Math.PI * 2 * i) / count;
            const distance = Math.random() * 100 + 50;
            const endX = x + Math.cos(angle) * distance;
            const endY = y + Math.sin(angle) * distance;
            
            const heart = document.createElement('div');
            heart.innerHTML = '❤️';
            heart.style.position = 'fixed';
            heart.style.left = x + 'px';
            heart.style.top = y + 'px';
            heart.style.color = heartColors[Math.floor(Math.random() * heartColors.length)];
            heart.style.fontSize = (Math.random() * 15 + 15) + 'px';
            heart.style.pointerEvents = 'none';
            heart.style.zIndex = '15';
            heart.style.transition = 'all 1s ease-out';
            document.body.appendChild(heart);
            
            setTimeout(() => {
                heart.style.left = endX + 'px';
                heart.style.top = endY + 'px';
                heart.style.opacity = '0';
                heart.style.transform = 'scale(0)';
            }, 10);
            
            setTimeout(() => {
                heart.remove();
            }, 1000);
        }, i * 30);
    }
}

// Create a shower of falling hearts
function createHeartShower() {
    const heart = document.createElement('div');
    heart.innerHTML = '❤️';
    heart.style.position = 'fixed';
    heart.style.left = Math.random() * window.innerWidth + 'px';
    heart.style.top = '-50px';
    heart.style.color = heartColors[Math.floor(Math.random() * heartColors.length)];
    heart.style.fontSize = (Math.random() * 20 + 20) + 'px';
    heart.style.pointerEvents = 'none';
    heart.style.zIndex = '5';
    heart.style.transition = 'top 4s linear, opacity 4s ease-in';
    document.body.appendChild(heart);
    
    setTimeout(() => {
        heart.style.top = (window.innerHeight + 50) + 'px';
        heart.style.opacity = '0';
    }, 10);
    
    setTimeout(() => {
        heart.remove();
    }, 4000);
}

// Start heart shower effect
let showerInterval;
function startHeartShower(interval = 500) {
    if (showerInterval) clearInterval(showerInterval);
    showerInterval = setInterval(createHeartShower, interval);
}

function stopHeartShower() {
    if (showerInterval) {
        clearInterval(showerInterval);
        showerInterval = null;
    }
}

// Export functions if needed
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        createHeartBurst,
        createHeartShower,
        startHeartShower,
        stopHeartShower
    };
}
