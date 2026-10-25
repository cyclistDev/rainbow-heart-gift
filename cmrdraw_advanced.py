import cv2
import mediapipe as mp
import numpy as np
import math
from collections import deque

# ========== CONFIGURATION ==========
class Config:
    # Camera settings
    CAMERA_WIDTH = 1280
    CAMERA_HEIGHT = 720
    CAMERA_FPS = 30
    
    # Hand tracking settings
    MAX_NUM_HANDS = 2  # Detect both hands
    MIN_DETECTION_CONFIDENCE = 0.7
    MIN_TRACKING_CONFIDENCE = 0.5
    
    # Gesture thresholds
    PINCH_THRESHOLD = 0.05  # Distance between thumb and index
    FIST_THRESHOLD = 0.3     # Average finger tip to palm distance
    OPEN_PALM_THRESHOLD = 0.5
    
    # Drawing settings
    BRUSH_SIZE_MIN = 1
    BRUSH_SIZE_MAX = 50
    DEFAULT_BRUSH_SIZE = 5
    SMOOTHING_WINDOW = 5  # Number of points for line smoothing
    
    # Canvas settings
    HEADER_HEIGHT = 100
    SIDEBAR_WIDTH = 100

# ========== HAND TRACKING ==========
class HandTracker:
    def __init__(self):
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            max_num_hands=Config.MAX_NUM_HANDS,
            min_detection_confidence=Config.MIN_DETECTION_CONFIDENCE,
            min_tracking_confidence=Config.MIN_TRACKING_CONFIDENCE
        )
        self.mp_draw = mp.solutions.drawing_utils
        
        # Track previous positions to reduce jitter
        self.previous_positions = {0: deque(maxlen=Config.SMOOTHING_WINDOW), 
                                   1: deque(maxlen=Config.SMOOTHING_WINDOW)}
    
    def process(self, frame):
        """Process frame and return hand landmarks with hand IDs"""
        img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(img_rgb)
        
        detected_hands = {}
        
        if results.multi_hand_landmarks and results.multi_handedness:
            for idx, (landmarks, handedness) in enumerate(zip(results.multi_hand_landmarks, results.multi_handedness)):
                # Determine hand label (Left/Right)
                hand_label = handedness.classification[0].label
                hand_id = 0 if hand_label == 'Left' else 1
                
                detected_hands[hand_id] = {
                    'landmarks': landmarks,
                    'label': hand_label
                }
        
        return detected_hands
    
    def smooth_position(self, hand_id, x, y):
        """Apply smoothing to reduce jitter"""
        if hand_id not in self.previous_positions:
            self.previous_positions[hand_id] = deque(maxlen=Config.SMOOTHING_WINDOW)
        
        self.previous_positions[hand_id].append((x, y))
        
        if len(self.previous_positions[hand_id]) < 2:
            return x, y
        
        # Calculate average position
        avg_x = sum(pos[0] for pos in self.previous_positions[hand_id]) / len(self.previous_positions[hand_id])
        avg_y = sum(pos[1] for pos in self.previous_positions[hand_id]) / len(self.previous_positions[hand_id])
        
        return int(avg_x), int(avg_y)

# ========== GESTURE RECOGNITION ==========
class GestureRecognizer:
    @staticmethod
    def is_fist(landmarks):
        """Check if hand is in fist position"""
        # Get finger tips and base positions
        tips = [8, 12, 16, 20]  # Index, middle, ring, pinky tips
        bases = [5, 9, 13, 17]   # Finger bases
        
        folded_count = 0
        for tip, base in zip(tips, bases):
            tip_y = landmarks.landmark[tip].y
            base_y = landmarks.landmark[base].y
            if tip_y > base_y:  # Finger is folded
                folded_count += 1
        
        return folded_count >= 3  # At least 3 fingers folded
    
    @staticmethod
    def is_index_only(landmarks):
        """Check if only index finger is extended"""
        index_tip = landmarks.landmark[8]
        middle_tip = landmarks.landmark[12]
        ring_tip = landmarks.landmark[16]
        pinky_tip = landmarks.landmark[20]
        
        index_extended = index_tip.y < landmarks.landmark[6].y
        middle_folded = middle_tip.y > landmarks.landmark[10].y
        ring_folded = ring_tip.y > landmarks.landmark[14].y
        pinky_folded = pinky_tip.y > landmarks.landmark[18].y
        
        return index_extended and middle_folded and ring_folded and pinky_fold
    
    @staticmethod
    def is_pinch(landmarks):
        """Check if thumb and index finger are pinching"""
        thumb_tip = landmarks.landmark[4]
        index_tip = landmarks.landmark[8]
        
        distance = math.sqrt((thumb_tip.x - index_tip.x)**2 + (thumb_tip.y - index_tip.y)**2)
        return distance < Config.PINCH_THRESHOLD
    
    @staticmethod
    def is_open_palm(landmarks):
        """Check if hand is in open palm position"""
        tips = [8, 12, 16, 20]
        bases = [5, 9, 13, 17]
        
        extended_count = 0
        for tip, base in zip(tips, bases):
            tip_y = landmarks.landmark[tip].y
            base_y = landmarks.landmark[base].y
            if tip_y < base_y:  # Finger is extended
                extended_count += 1
        
        return extended_count >= 3
    
    @staticmethod
    def is_two_fingers(landmarks):
        """Check if two fingers are extended (index and middle)"""
        index_tip = landmarks.landmark[8]
        middle_tip = landmarks.landmark[12]
        ring_tip = landmarks.landmark[16]
        pinky_tip = landmarks.landmark[20]
        
        index_extended = index_tip.y < landmarks.landmark[6].y
        middle_extended = middle_tip.y < landmarks.landmark[10].y
        ring_folded = ring_tip.y > landmarks.landmark[14].y
        pinky_folded = pinky_tip.y > landmarks.landmark[18].y
        
        return index_extended and middle_extended and ring_folded and pinky_fold
    
    @staticmethod
    def detect_gesture(landmarks):
        """Detect current gesture"""
        if GestureRecognizer.is_pinch(landmarks):
            return 'pinch'
        elif GestureRecognizer.is_index_only(landmarks):
            return 'index'
        elif GestureRecognizer.is_two_fingers(landmarks):
            return 'two_fingers'
        elif GestureRecognizer.is_open_palm(landmarks):
            return 'open_palm'
        elif GestureRecognizer.is_fist(landmarks):
            return 'fist'
        else:
            return 'unknown'

# ========== DRAWING CANVAS ==========
class DrawingCanvas:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.canvas = np.zeros((height, width, 3), np.uint8)
        self.undo_stack = []
        self.redo_stack = []
        self.max_undo = 20
        
        # Drawing state for each hand
        self.drawing_state = {
            0: {'drawing': False, 'prev_pos': None, 'color': None, 'brush_size': Config.DEFAULT_BRUSH_SIZE},
            1: {'drawing': False, 'prev_pos': None, 'color': None, 'brush_size': Config.DEFAULT_BRUSH_SIZE}
        }
        
        # Colors
        self.colors = [
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
            (0, 0, 0),        # Black (eraser)
        ]
        self.current_color = self.colors[0]
        self.brush_size = Config.DEFAULT_BRUSH_SIZE
        self.is_eraser = False
    
    def save_state(self):
        """Save current canvas state for undo"""
        if len(self.undo_stack) >= self.max_undo:
            self.undo_stack.pop(0)
        self.undo_stack.append(self.canvas.copy())
        self.redo_stack.clear()
    
    def undo(self):
        """Undo last action"""
        if self.undo_stack:
            self.redo_stack.append(self.canvas.copy())
            self.canvas = self.undo_stack.pop()
    
    def redo(self):
        """Redo last undone action"""
        if self.redo_stack:
            self.undo_stack.append(self.canvas.copy())
            self.canvas = self.redo_stack.pop()
    
    def clear(self):
        """Clear canvas"""
        self.save_state()
        self.canvas = np.zeros((self.height, self.width, 3), np.uint8)
    
    def draw_line(self, hand_id, x1, y1, x2, y2, color, brush_size):
        """Draw smooth line on canvas"""
        color_to_use = color if not self.is_eraser else (0, 0, 0)
        cv2.line(self.canvas, (x1, y1), (x2, y2), color_to_use, int(brush_size * 2))
        self.drawing_state[hand_id]['prev_pos'] = (x2, y2)
    
    def set_color(self, color):
        """Set current drawing color"""
        self.current_color = color
        self.is_eraser = False
    
    def set_eraser(self):
        """Set eraser mode"""
        self.is_eraser = True

# ========== MAIN APPLICATION ==========
class DrawingApp:
    def __init__(self):
        self.cap = cv2.VideoCapture(0)
        self.cap.set(3, Config.CAMERA_WIDTH)
        self.cap.set(4, Config.CAMERA_HEIGHT)
        
        self.tracker = HandTracker()
        self.canvas = None
        self.frame_count = 0
        
        # Mode: 'draw', 'select_color', 'pause'
        self.mode = 'draw'
        self.selected_color_index = 0
    
    def run(self):
        try:
            while True:
                success, frame = self.cap.read()
                if not success:
                    print("Failed to read from camera")
                    break
                
                frame = cv2.flip(frame, 1)
                h, w, _ = frame.shape
                
                # Initialize canvas
                if self.canvas is None:
                    self.canvas = DrawingCanvas(w, h)
                
                # Process hands
                detected_hands = self.tracker.process(frame)
                
                # Draw UI
                self.draw_ui(frame, w, h)
                
                # Process each detected hand
                for hand_id, hand_data in detected_hands.items():
                    landmarks = hand_data['landmarks']
                    gesture = GestureRecognizer.detect_gesture(landmarks)
                    
                    # Get index finger position
                    index_finger = landmarks.landmark[8]
                    x, y = int(index_finger.x * w), int(index_finger.y * h)
                    
                    # Apply smoothing
                    x, y = self.tracker.smooth_position(hand_id, x, y)
                    
                    # Handle gestures
                    self.handle_gesture(hand_id, gesture, x, y, frame, w, h)
                    
                    # Draw hand landmarks
                    self.tracker.mp_draw.draw_landmarks(
                        frame, landmarks, self.tracker.mp_hands.HAND_CONNECTIONS
                    )
                    
                    # Display gesture status
                    gesture_text = f"Hand {hand_id}: {gesture.upper()}"
                    cv2.putText(frame, gesture_text, (10, 30 + hand_id * 30), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                
                # Combine canvas and frame
                frame = cv2.addWeighted(frame, 0.7, self.canvas.canvas, 0.3, 0)
                
                # Display mode
                cv2.putText(frame, f"Mode: {self.mode.upper()}", (10, h - 20), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
                
                cv2.imshow("Advanced Hand Drawing", frame)
                
                # Keyboard controls
                key = cv2.waitKey(1)
                if key == ord('q'):
                    break
                elif key == ord('u'):
                    self.canvas.undo()
                elif key == ord('r'):
                    self.canvas.redo()
                elif key == ord('c'):
                    self.canvas.clear()
                elif key == ord('['):
                    self.canvas.brush_size = max(Config.BRUSH_SIZE_MIN, self.canvas.brush_size - 1)
                elif key == ord(']'):
                    self.canvas.brush_size = min(Config.BRUSH_SIZE_MAX, self.canvas.brush_size + 1)
                elif key == ord('e'):
                    self.canvas.set_eraser()
                elif key == ord('s'):
                    cv2.imwrite('drawing.png', self.canvas.canvas)
                    print("Drawing saved!")
                
                self.frame_count += 1
        
        except Exception as e:
            print(f"Error: {e}")
        finally:
            self.cap.release()
            cv2.destroyAllWindows()
    
    def draw_ui(self, frame, w, h):
        """Draw user interface"""
        # Header
        cv2.rectangle(frame, (0, 0), (w, Config.HEADER_HEIGHT), (30, 30, 30), -1)
        
        # Color buttons
        button_width = w // len(self.canvas.colors)
        for i, color in enumerate(self.canvas.colors):
            cv2.rectangle(frame, (i * button_width, 0), ((i + 1) * button_width, Config.HEADER_HEIGHT), color, -1)
            label = f"C{i+1}"
            text_color = (0, 0, 0) if i == 9 else (255, 255, 255)
            cv2.putText(frame, label, (i * button_width + 10, Config.HEADER_HEIGHT // 2), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.4, text_color, 1)
        
        # Instructions
        instructions = [
            "Gestures: Index=Draw, Fist=Stop, Pinch=Select, OpenPalm=Pause",
            "Keys: [ ] brush size, U=undo, R=redo, C=clear, E=eraser, S=save, Q=quit"
        ]
        
        for i, instruction in enumerate(instructions):
            cv2.putText(frame, instruction, (10, h - 50 + i * 25), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
    
    def handle_gesture(self, hand_id, gesture, x, y, frame, w, h):
        """Handle different gestures"""
        # Check if in header area (color selection)
        if y < Config.HEADER_HEIGHT:
            if gesture == 'pinch':
                button_width = w // len(self.canvas.colors)
                color_index = int(x // button_width)
                if color_index < len(self.canvas.colors):
                    self.canvas.set_color(self.canvas.colors[color_index])
                    self.mode = 'draw'
            return
        
        # Handle gestures based on mode
        if gesture == 'index' and self.mode == 'draw':
            prev_pos = self.canvas.drawing_state[hand_id]['prev_pos']
            if prev_pos:
                # Calculate distance to avoid too many points
                distance = math.sqrt((x - prev_pos[0])**2 + (y - prev_pos[1])**2)
                if distance > 5:
                    self.canvas.draw_line(hand_id, prev_pos[0], prev_pos[1], x, y, 
                                         self.canvas.current_color, self.canvas.brush_size)
            else:
                self.canvas.drawing_state[hand_id]['prev_pos'] = (x, y)
        
        elif gesture == 'fist':
            self.canvas.drawing_state[hand_id]['prev_pos'] = None
            self.canvas.drawing_state[hand_id]['drawing'] = False
        
        elif gesture == 'open_palm':
            self.mode = 'pause'
            self.canvas.drawing_state[hand_id]['prev_pos'] = None
        
        elif gesture == 'two_fingers':
            # Could be used for additional actions
            pass

if __name__ == "__main__":
    app = DrawingApp()
    app.run()
