import cv2
import numpy as np
import math

# Initialize webcam
cap = cv2.VideoCapture(0)
cap.set(3, 1280)
cap.set(4, 720)

# Heart colors
heart_colors = [
    (0, 0, 255),      # Red
    (255, 0, 255),    # Magenta
    (255, 20, 147),   # Deep Pink
    (255, 105, 180),  # Hot Pink
    (255, 182, 193),  # Light Pink
    (255, 192, 203),  # Pink
]

current_color = heart_colors[0]
xp, yp = 0, 0
header_height = 100
drawing = False

canvas = None

# Function to draw heart shape
def draw_heart(canvas, x, y, size, color):
    points = []
    for t in np.linspace(0, 2 * np.pi, 100):
        # Heart parametric equation
        heart_x = 16 * (np.sin(t) ** 3)
        heart_y = 13 * np.cos(t) - 5 * np.cos(2*t) - 2 * np.cos(3*t) - np.cos(4*t)
        
        # Scale and position
        px = int(x + heart_x * size)
        py = int(y - heart_y * size)
        points.append((px, py))
    
    # Draw the heart
    if len(points) > 2:
        cv2.fillPoly(canvas, [np.array(points)], color)

# Mouse callback function
def mouse_callback(event, x, y, flags, param):
    global xp, yp, drawing, current_color
    
    if event == cv2.EVENT_LBUTTONDOWN:
        # Check if clicking in header area (color selection)
        if y < header_height:
            button_width = 1280 // len(heart_colors)
            color_index = int(x // button_width)
            if color_index < len(heart_colors):
                current_color = heart_colors[color_index]
        else:
            drawing = True
            xp, yp = x, y
            draw_heart(canvas, x, y, 10, current_color)
    
    elif event == cv2.EVENT_LBUTTONUP:
        drawing = False
    
    elif event == cv2.EVENT_MOUSEMOVE:
        if drawing:
            # Calculate distance to avoid too many hearts
            distance = math.sqrt((x - xp)**2 + (y - yp)**2)
            if distance > 30:
                draw_heart(canvas, x, y, 10, current_color)
                xp, yp = x, y

cv2.namedWindow("Heart Drawing")
cv2.setMouseCallback("Heart Drawing", mouse_callback)

while True:
    success, frame = cap.read()
    if not success:
        break

    frame = cv2.flip(frame, 1)
    h, w, _ = frame.shape

    # Initialize canvas
    if canvas is None:
        canvas = np.zeros((h, w, 3), np.uint8)

    # Draw header
    cv2.rectangle(frame, (0, 0), (w, header_height), (0, 0, 0), -1)
    
    # Draw color buttons
    button_width = w // len(heart_colors)
    for i, color in enumerate(heart_colors):
        cv2.rectangle(frame, (i * button_width, 0), ((i + 1) * button_width, header_height), color, -1)
        cv2.putText(frame, f"Color {i+1}", (i * button_width + 10, header_height // 2), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)

    # Draw instruction
    cv2.putText(frame, "Click and drag to draw hearts! Press 'c' to clear, 'q' to quit", (10, h - 20), 
               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

    # Combine canvas and frame
    frame = cv2.addWeighted(frame, 0.7, canvas, 0.3, 0)

    cv2.imshow("Heart Drawing", frame)

    # Press 'q' to quit, 'c' to clear canvas
    key = cv2.waitKey(1)
    if key == ord('q'):
        break
    elif key == ord('c'):
        canvas = np.zeros((h, w, 3), np.uint8)
        xp, yp = 0, 0

cap.release()
cv2.destroyAllWindows()
