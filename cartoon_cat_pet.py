import cv2
import mediapipe as mp
import numpy as np
import math

# ========== CONFIGURATION ==========
class CatConfig:
    # Camera settings
    CAMERA_WIDTH = 1280
    CAMERA_HEIGHT = 720
    
    # Hand tracking
    MAX_NUM_HANDS = 1
    MIN_DETECTION_CONFIDENCE = 0.7
    MIN_TRACKING_CONFIDENCE = 0.5
    
    # Cat animation settings
    CAT_SIZE = 150
    EYE_SIZE = 20
    PUPIL_SIZE = 8
    WHISKER_LENGTH = 40
    
    # Interaction thresholds
    PINCH_THRESHOLD = 0.05
    WAVE_THRESHOLD = 0.3

# ========== CARTOON CAT CLASS ==========
class CartoonCat:
    def __init__(self, x, y, size):
        self.x = x
        self.y = y
        self.size = size
        self.target_x = x
        self.target_y = y
        self.blink_timer = 0
        self.is_blinking = False
        self.tail_angle = 0
        self.tail_direction = 1
        self.mood = 'happy'  # happy, curious, excited
        self.purr_timer = 0
    
    def update(self, hand_x, hand_y, hand_detected):
        """Update cat position and animation"""
        # Move towards hand if detected
        if hand_detected:
            self.target_x = hand_x
            self.target_y = hand_y
            self.mood = 'curious'
        else:
            # Return to center if no hand
            self.target_x = CatConfig.CAMERA_WIDTH // 2
            self.target_y = CatConfig.CAMERA_HEIGHT // 2
            self.mood = 'happy'
        
        # Smooth movement
        self.x += (self.target_x - self.x) * 0.1
        self.y += (self.target_y - self.y) * 0.1
        
        # Animate tail
        self.tail_angle += 0.05 * self.tail_direction
        if abs(self.tail_angle) > 0.5:
            self.tail_direction *= -1
        
        # Blink animation
        self.blink_timer += 1
        if self.blink_timer > 100:
            self.is_blinking = True
            if self.blink_timer > 105:
                self.is_blinking = False
                self.blink_timer = 0
        
        # Purr animation
        self.purr_timer += 0.1
    
    def draw(self, frame):
        """Draw cartoon cat on frame"""
        # Cat body color based on mood
        if self.mood == 'happy':
            body_color = (255, 200, 150)  # Orange
        elif self.mood == 'curious':
            body_color = (200, 200, 200)  # Gray
        else:  # excited
            body_color = (255, 180, 180)  # Pink
        
        # Draw body (ellipse)
        body_width = int(self.size * 1.2)
        body_height = int(self.size * 0.8)
        cv2.ellipse(frame, (int(self.x), int(self.y)), 
                    (body_width // 2, body_height // 2), 0, 0, 360, body_color, -1)
        
        # Draw head (circle)
        head_radius = int(self.size * 0.4)
        head_y = int(self.y - self.size * 0.3)
        cv2.circle(frame, (int(self.x), head_y), head_radius, body_color, -1)
        
        # Draw ears (triangles)
        ear_size = int(self.size * 0.25)
        ear_height = int(self.size * 0.3)
        
        # Left ear
        left_ear_x = int(self.x - head_radius + 10)
        left_ear_y = head_y - ear_height + 10
        pts_left = np.array([
            [left_ear_x - ear_size // 2, left_ear_y + ear_height],
            [left_ear_x, left_ear_y],
            [left_ear_x + ear_size // 2, left_ear_y + ear_height]
        ], np.int32)
        cv2.fillPoly(frame, [pts_left], body_color)
        
        # Right ear
        right_ear_x = int(self.x + head_radius - 10)
        right_ear_y = head_y - ear_height + 10
        pts_right = np.array([
            [right_ear_x - ear_size // 2, right_ear_y + ear_height],
            [right_ear_x, right_ear_y],
            [right_ear_x + ear_size // 2, right_ear_y + ear_height]
        ], np.int32)
        cv2.fillPoly(frame, [pts_right], body_color)
        
        # Draw eyes
        eye_offset_x = int(head_radius * 0.4)
        eye_y = head_y - 5
        
        if self.is_blinking:
            # Draw closed eyes (lines)
            cv2.line(frame, (int(self.x - eye_offset_x - 10), eye_y), 
                    (int(self.x - eye_offset_x + 10), eye_y), (0, 0, 0), 3)
            cv2.line(frame, (int(self.x + eye_offset_x - 10), eye_y), 
                    (int(self.x + eye_offset_x + 10), eye_y), (0, 0, 0), 3)
        else:
            # Draw eyes (circles with pupils)
            # Left eye
            cv2.circle(frame, (int(self.x - eye_offset_x), eye_y), CatConfig.EYE_SIZE, (255, 255, 255), -1)
            # Left pupil (follows hand slightly)
            pupil_offset_x = int((self.target_x - self.x) * 0.05)
            pupil_offset_y = int((self.target_y - head_y) * 0.05)
            cv2.circle(frame, (int(self.x - eye_offset_x + pupil_offset_x), 
                             eye_y + pupil_offset_y), CatConfig.PUPIL_SIZE, (0, 0, 0), -1)
            
            # Right eye
            cv2.circle(frame, (int(self.x + eye_offset_x), eye_y), CatConfig.EYE_SIZE, (255, 255, 255), -1)
            cv2.circle(frame, (int(self.x + eye_offset_x + pupil_offset_x), 
                             eye_y + pupil_offset_y), CatConfig.PUPIL_SIZE, (0, 0, 0), -1)
        
        # Draw nose (small triangle)
        nose_y = head_y + 15
        pts_nose = np.array([
            [int(self.x - 8), nose_y],
            [int(self.x + 8), nose_y],
            [int(self.x), nose_y + 10]
        ], np.int32)
        cv2.fillPoly(frame, [pts_nose], (255, 150, 150))
        
        # Draw mouth
        mouth_y = nose_y + 15
        cv2.line(frame, (int(self.x), mouth_y), (int(self.x - 10), mouth_y + 10), (0, 0, 0), 2)
        cv2.line(frame, (int(self.x), mouth_y), (int(self.x + 10), mouth_y + 10), (0, 0, 0), 2)
        
        # Draw whiskers
        whisker_y = nose_y
        for i in range(3):
            # Left whiskers
            cv2.line(frame, (int(self.x - head_radius), whisker_y + i * 10), 
                    (int(self.x - head_radius - CatConfig.WHISKER_LENGTH), whisker_y + i * 10 - 5), 
                    (0, 0, 0), 2)
            # Right whiskers
            cv2.line(frame, (int(self.x + head_radius), whisker_y + i * 10), 
                    (int(self.x + head_radius + CatConfig.WHISKER_LENGTH), whisker_y + i * 10 - 5), 
                    (0, 0, 0), 2)
        
        # Draw tail (wagging line)
        tail_start_x = int(self.x + body_width // 2)
        tail_start_y = int(self.y + body_height // 2)
        tail_end_x = tail_start_x + int(math.sin(self.tail_angle) * 50)
        tail_end_y = tail_start_y - 40 + int(math.cos(self.tail_angle) * 20)
        cv2.line(frame, (tail_start_x, tail_start_y), (tail_end_x, tail_end_y), body_color, 8)
        
        # Draw paws
        paw_offset = int(body_width * 0.3)
        paw_y = int(self.y + body_height // 2 - 10)
        cv2.ellipse(frame, (int(self.x - paw_offset), paw_y), (15, 10), 0, 0, 360, body_color, -1)
        cv2.ellipse(frame, (int(self.x + paw_offset), paw_y), (15, 10), 0, 0, 360, body_color, -1)
        
        # Draw mood indicator
        mood_colors = {'happy': (0, 255, 0), 'curious': (255, 255, 0), 'excited': (255, 0, 255)}
        cv2.circle(frame, (int(self.x), int(self.y - self.size * 0.8)), 8, mood_colors[self.mood], -1)

# ========== HAND TRACKING ==========
class HandTracker:
    def __init__(self):
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            max_num_hands=CatConfig.MAX_NUM_HANDS,
            min_detection_confidence=CatConfig.MIN_DETECTION_CONFIDENCE,
            min_tracking_confidence=CatConfig.MIN_TRACKING_CONFIDENCE
        )
        self.mp_draw = mp.solutions.drawing_utils
    
    def process(self, frame):
        """Process frame and return hand position"""
        img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(img_rgb)
        
        hand_x, hand_y = None, None
        hand_detected = False
        
        if results.multi_hand_landmarks:
            for landmarks in results.multi_hand_landmarks:
                # Get palm center (average of all landmarks)
                x_coords = [lm.x for lm in landmarks.landmark]
                y_coords = [lm.y for lm in landmarks.landmark]
                
                hand_x = (min(x_coords) + max(x_coords)) / 2
                hand_y = (min(y_coords) + max(y_coords)) / 2
                
                hand_detected = True
                
                # Draw hand landmarks
                self.mp_draw.draw_landmarks(frame, landmarks, self.mp_hands.HAND_CONNECTIONS)
                break
        
        return hand_x, hand_y, hand_detected

# ========== MAIN APPLICATION ==========
class CatPetApp:
    def __init__(self):
        self.cap = cv2.VideoCapture(0)
        self.cap.set(3, CatConfig.CAMERA_WIDTH)
        self.cap.set(4, CatConfig.CAMERA_HEIGHT)
        
        self.tracker = HandTracker()
        self.cat = CartoonCat(CatConfig.CAMERA_WIDTH // 2, CatConfig.CAMERA_HEIGHT // 2, CatConfig.CAT_SIZE)
        
        self.frame_count = 0
    
    def run(self):
        try:
            while True:
                success, frame = self.cap.read()
                if not success:
                    print("Failed to read from camera")
                    break
                
                frame = cv2.flip(frame, 1)
                h, w, _ = frame.shape
                
                # Process hands
                hand_x, hand_y, hand_detected = self.tracker.process(frame)
                
                # Convert hand coordinates to screen coordinates
                if hand_detected:
                    screen_x = int(hand_x * w)
                    screen_y = int(hand_y * h)
                else:
                    screen_x, screen_y = None, None
                
                # Update and draw cat
                self.cat.update(screen_x, screen_y, hand_detected)
                self.cat.draw(frame)
                
                # Draw instructions
                self.draw_instructions(frame, w, h)
                
                # Display mood
                mood_text = f"Cat Mood: {self.cat.mood.upper()}"
                cv2.putText(frame, mood_text, (10, 50), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
                
                cv2.imshow("Cartoon Cat Pet", frame)
                
                # Keyboard controls
                key = cv2.waitKey(1)
                if key == ord('q'):
                    break
                elif key == ord('h'):
                    self.cat.mood = 'happy'
                elif key == ord('c'):
                    self.cat.mood = 'curious'
                elif key == ord('e'):
                    self.cat.mood = 'excited'
                
                self.frame_count += 1
        
        except Exception as e:
            print(f"Error: {e}")
        finally:
            self.cap.release()
            cv2.destroyAllWindows()
    
    def draw_instructions(self, frame, w, h):
        """Draw instructions on screen"""
        instructions = [
            "Move your hand to attract the cat!",
            "Press 'q' to quit",
            "Press 'h' for happy, 'c' for curious, 'e' for excited"
        ]
        
        for i, instruction in enumerate(instructions):
            cv2.putText(frame, instruction, (10, h - 60 + i * 25), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

if __name__ == "__main__":
    app = CatPetApp()
    app.run()
