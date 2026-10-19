import cv2
import mediapipe as mp
import numpy as np
import math

# Initialize webcam
cap = cv2.VideoCapture(0)
cap.set(3, 1280)
cap.set(4, 720)

# Initialize mediapipe hands
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    max_num_hands=1,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.5
)
mp_draw = mp.solutions.drawing_utils

# Drawing colors
colors = [
    (0, 0, 255),      # Red
    (255, 0, 255),    # Magenta
    (255, 20, 147),   # Deep Pink
    (255, 105, 180),  # Hot Pink
    (255, 182, 193),  # Light Pink
    (255, 192, 203),  # Pink
    (0, 255, 0),      # Green
    (255, 255, 0),    # Yellow
    (0, 255, 255),    # Cyan
    (255, 255, 255),  # White
    (0, 0, 0),        # Black
]

current_color = colors[0]
brush_size = 5
xp, yp = 0, 0
header_height = 100
sidebar_width = 80

canvas = None
is_drawing = False
zoom_level = 1.0

# Function to check if hand is in drawing mode (one finger up)
def is_drawing_gesture(hand_landmarks):
    # Check if only index finger is extended
    # Landmarks: 0=wrist, 8=index tip, 12=middle tip, 14=ring tip, 20=pinky tip
    
    # Get finger tip positions
    index_tip = hand_landmarks.landmark[8]
    middle_tip = hand_landmarks.landmark[12]
    ring_tip = hand_landmarks.landmark[16]
    pinky_tip = hand_landmarks.landmark[20]
    wrist = hand_landmarks.landmark[0]
    
    # Check if other fingers are folded (closer to wrist than index)
    index_extended = index_tip.y < hand_landmarks.landmark[6].y
    middle_folded = middle_tip.y > hand_landmarks.landmark[10].y
    ring_folded = ring_tip.y > hand_landmarks.landmark[14].y
    pinky_folded = pinky_tip.y > hand_landmarks.landmark[18].y
    
    # Return True if only index finger is extended
    return index_extended and middle_folded and ring_folded and pinky_folded

# Function to check for zoom gesture (two fingers apart)
def get_zoom_gesture(hand_landmarks):
    # Distance between thumb and index finger
    thumb_tip = hand_landmarks.landmark[4]
    index_tip = hand_landmarks.landmark[8]
    
    distance = math.sqrt((thumb_tip.x - index_tip.x)**2 + (thumb_tip.y - index_tip.y)**2)
    return distance

while True:
    success, frame = cap.read()
    if not success:
        break

    frame = cv2.flip(frame, 1)
    h, w, _ = frame.shape

    # Initialize canvas
    if canvas is None:
        canvas = np.zeros((h, w, 3), np.uint8)

    # Convert to RGB for mediapipe
    img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(img_rgb)

    # Draw header
    cv2.rectangle(frame, (0, 0), (w, header_height), (30, 30, 30), -1)
    
    # Draw color buttons
    button_width = w // len(colors)
    for i, color in enumerate(colors):
        cv2.rectangle(frame, (i * button_width, 0), ((i + 1) * button_width, header_height), color, -1)
        label = f"C{i+1}"
        text_color = (0, 0, 0) if i == 9 else (255, 255, 255)
        cv2.putText(frame, label, (i * button_width + 10, header_height // 2), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.4, text_color, 1)

    # Draw sidebar with buttons
    cv2.rectangle(frame, (w - sidebar_width, header_height), (w, h), (40, 40, 40), -1)
    
    # Clear button
    cv2.rectangle(frame, (w - sidebar_width + 10, header_height + 20), (w - 10, header_height + 70), (255, 0, 0), -1)
    cv2.putText(frame, "CLR", (w - sidebar_width + 15, header_height + 50), 
               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
    
    # Save button
    cv2.rectangle(frame, (w - sidebar_width + 10, header_height + 90), (w - 10, header_height + 140), (0, 255, 0), -1)
    cv2.putText(frame, "SAVE", (w - sidebar_width + 12, header_height + 120), 
               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
    
    # Zoom controls
    cv2.putText(frame, "Zoom:", (w - sidebar_width + 10, header_height + 180), 
               cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)
    cv2.putText(frame, f"{zoom_level:.1f}x", (w - sidebar_width + 10, header_height + 200), 
               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 2)

    # Draw brush size indicator
    cv2.putText(frame, f"Brush: {brush_size}", (10, h - 60), 
               cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

    # Draw gesture status
    gesture_text = "FIST - STOP" if not is_drawing else "1 FINGER - DRAW"
    gesture_color = (0, 255, 0) if is_drawing else (0, 0, 255)
    cv2.putText(frame, gesture_text, (10, h - 40), 
               cv2.FONT_HERSHEY_SIMPLEX, 0.7, gesture_color, 2)
    
    cv2.putText(frame, "Press 'q' to quit", (10, h - 20), 
               cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

    # Process hand landmarks
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            # Check gesture
            is_drawing = is_drawing_gesture(hand_landmarks)
            
            # Get index finger tip (landmark 8)
            index_finger = hand_landmarks.landmark[8]
            x, y = int(index_finger.x * w), int(index_finger.y * h)

            # Check if finger is in header area (color selection)
            if y < header_height:
                color_index = int(x // button_width)
                if color_index < len(colors):
                    current_color = colors[color_index]
            # Check if finger is in sidebar (button click)
            elif x > w - sidebar_width:
                # Clear button
                if header_height + 20 < y < header_height + 70:
                    canvas = np.zeros((h, w, 3), np.uint8)
                    xp, yp = 0, 0
                # Save button
                elif header_height + 90 < y < header_height + 140:
                    cv2.imwrite('love_drawing.png', canvas)
                    print("Drawing saved as 'love_drawing.png'")
            # Drawing area
            elif is_drawing:
                if xp != 0 and yp != 0:
                    distance = math.sqrt((x - xp)**2 + (y - yp)**2)
                    if distance > 5:
                        cv2.line(canvas, (xp, yp), (x, y), current_color, int(brush_size * 2 * zoom_level))
                        xp, yp = x, y
                else:
                    xp, yp = x, y
            else:
                xp, yp = 0, 0

            # Draw hand landmarks
            mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

    # Combine canvas and frame
    frame = cv2.addWeighted(frame, 0.7, canvas, 0.3, 0)

    cv2.imshow("Love Drawing App - Hand Gesture", frame)

    # Key controls
    key = cv2.waitKey(1)
    if key == ord('q'):
        break
    elif key == ord('+') or key == ord('='):
        zoom_level = min(zoom_level + 0.1, 3.0)
    elif key == ord('-') or key == ord('_'):
        zoom_level = max(zoom_level - 0.1, 0.5)
    elif key == ord('['):
        brush_size = max(brush_size - 1, 1)
    elif key == ord(']'):
        brush_size = min(brush_size + 1, 50)

cap.release()
cv2.destroyAllWindows()
