import math
import sys
import time

import cv2
import mediapipe as mp
import numpy as np

from cat_sprite import AnimatedCatSprite


CAMERA_INDEX = 0
MAX_HANDS = 2
MIN_DETECTION_CONFIDENCE = 0.65
MIN_TRACKING_CONFIDENCE = 0.55
POSITION_SMOOTHING = 0.18
PINCH_DISTANCE_RATIO = 0.38

WINDOW_NAME = "Finger Cat - Chibi Sprite"
BUTTON_WIDTH = 170
BUTTON_HEIGHT = 44
BACKGROUND = (32, 26, 42)
WHITE = (250, 245, 235)
PINK = (170, 130, 255)


def distance(point_a, point_b):
    return math.hypot(point_a.x - point_b.x, point_a.y - point_b.y)


def get_gesture(hand_landmarks):
    points = hand_landmarks.landmark
    extended = [
        points[tip].y < points[pip].y - 0.015
        for tip, pip in ((8, 6), (12, 10), (16, 14), (20, 18))
    ]
    palm_width = distance(points[5], points[17])
    pinching = palm_width > 0 and distance(points[4], points[8]) < palm_width * PINCH_DISTANCE_RATIO
    if pinching:
        return "PINCH"
    if all(extended):
        return "OPEN PALM"
    if extended[0] and not any(extended[1:]):
        return "POINT"
    if not any(extended):
        return "FIST"
    return "HAND"


def draw_heart(frame, center, size, color):
    x, y = center
    radius = max(2, size // 4)
    cv2.circle(frame, (x - radius, y), radius, color, -1, cv2.LINE_AA)
    cv2.circle(frame, (x + radius, y), radius, color, -1, cv2.LINE_AA)
    points = np.array([
        (x - radius * 2, y),
        (x + radius * 2, y),
        (x, y + size),
    ], dtype=np.int32)
    cv2.fillConvexPoly(frame, points, color, cv2.LINE_AA)


def draw_overlay(frame, enabled, button_rect, gesture, hand_present):
    x1, y1, x2, y2 = button_rect
    button_color = (75, 145, 90) if enabled else (75, 75, 105)
    cv2.rectangle(frame, (x1, y1), (x2, y2), button_color, -1, cv2.LINE_AA)
    cv2.rectangle(frame, (x1, y1), (x2, y2), WHITE, 1, cv2.LINE_AA)
    button_label = "CAT: ON" if enabled else "CAT: OFF"
    cv2.putText(frame, button_label, (x1 + 17, y1 + 29), cv2.FONT_HERSHEY_SIMPLEX, 0.65, WHITE, 2, cv2.LINE_AA)

    cv2.rectangle(frame, (12, 12), (335, 92), BACKGROUND, -1)
    cv2.putText(frame, "FINGER CAT", (24, 39), cv2.FONT_HERSHEY_SIMPLEX, 0.68, WHITE, 2, cv2.LINE_AA)
    if hand_present:
        message = f"Hand: {gesture}  |  Pet: {'following' if enabled else 'disabled'}"
    else:
        message = f"No hand detected  |  Pet: {'waiting for you' if enabled else 'disabled'}"
    cv2.putText(frame, message, (24, 72), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (220, 220, 230), 1, cv2.LINE_AA)
    cv2.putText(frame, "Index finger: follow  |  Pinch: heart  |  P: toggle  |  Q: quit",
                (18, frame.shape[0] - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, WHITE, 1, cv2.LINE_AA)


def run():
    sprite = AnimatedCatSprite()
    started_at = time.monotonic()
    camera = cv2.VideoCapture(CAMERA_INDEX)
    if not camera.isOpened():
        camera.release()
        raise RuntimeError(f"Could not open camera {CAMERA_INDEX}. Check that it is connected and available.")

    camera.set(cv2.CAP_PROP_FRAME_WIDTH, 960)
    camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 540)
    camera.set(cv2.CAP_PROP_BUFFERSIZE, 1)

    hands_model = mp.solutions.hands.Hands(
        static_image_mode=False,
        max_num_hands=MAX_HANDS,
        model_complexity=0,
        min_detection_confidence=MIN_DETECTION_CONFIDENCE,
        min_tracking_confidence=MIN_TRACKING_CONFIDENCE,
    )
    drawing_utils = mp.solutions.drawing_utils
    state = {
        "enabled": True,
        "button_rect": (0, 0, BUTTON_WIDTH, BUTTON_HEIGHT),
        "pet_x": None,
        "pet_y": None,
        "hearts_until": 0.0,
        "last_pinch": False,
    }

    def on_mouse(event, x, y, flags, parameter):
        if event == cv2.EVENT_LBUTTONUP:
            x1, y1, x2, y2 = state["button_rect"]
            if x1 <= x <= x2 and y1 <= y <= y2:
                state["enabled"] = not state["enabled"]

    cv2.namedWindow(WINDOW_NAME)
    cv2.setMouseCallback(WINDOW_NAME, on_mouse)

    try:
        failed_frames = 0
        while True:
            success, frame = camera.read()
            if not success:
                failed_frames += 1
                if failed_frames >= 3:
                    print("Camera stopped returning frames.")
                    break
                continue
            failed_frames = 0

            frame = cv2.flip(frame, 1)
            height, width, _ = frame.shape
            button_rect = (width - BUTTON_WIDTH - 18, 16, width - 18, 16 + BUTTON_HEIGHT)
            state["button_rect"] = button_rect

            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            rgb_frame.flags.writeable = False
            results = hands_model.process(rgb_frame)
            hand_landmarks_list = results.multi_hand_landmarks or []
            hand_labels = results.multi_handedness or []
            active_gesture = "WAITING"
            target = None
            pinching = False

            if hand_landmarks_list:
                hand = hand_landmarks_list[0]
                gesture = get_gesture(hand)
                active_gesture = gesture
                pinching = gesture == "PINCH"
                index_tip = hand.landmark[8]
                tracking_scale = min(1.0, width / 960, height / 540)
                target = (
                    int(index_tip.x * width),
                    int(index_tip.y * height) - int(65 * tracking_scale),
                )

                for index, landmarks in enumerate(hand_landmarks_list):
                    drawing_utils.draw_landmarks(
                        frame,
                        landmarks,
                        mp.solutions.hands.HAND_CONNECTIONS,
                    )
                    if index < len(hand_labels) and hand_labels[index].classification:
                        label = hand_labels[index].classification[0].label
                        wrist = landmarks.landmark[0]
                        cv2.putText(
                            frame,
                            label,
                            (int(wrist.x * width), int(wrist.y * height) + 25),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.55,
                            (0, 255, 255),
                            2,
                            cv2.LINE_AA,
                        )

                if pinching and not state["last_pinch"]:
                    state["hearts_until"] = time.monotonic() + 1.2
                state["last_pinch"] = pinching
            else:
                state["last_pinch"] = False

            if target is None:
                target = (width // 2, height - int(165 * min(1.0, width / 960, height / 540)))

            if state["pet_x"] is None:
                state["pet_x"], state["pet_y"] = target
            else:
                state["pet_x"] += POSITION_SMOOTHING * (target[0] - state["pet_x"])
                state["pet_y"] += POSITION_SMOOTHING * (target[1] - state["pet_y"])
            display_width = max(120, int(260 * min(1.0, width / 960, height / 540)))
            display_height = round(display_width * sprite.height / sprite.width)
            pet_center = (
                max(display_width // 2, min(width - display_width // 2, int(state["pet_x"]))),
                max(display_height // 2, min(height - display_height // 2, int(state["pet_y"]))),
            )

            if state["enabled"]:
                sprite.draw(frame, pet_center, time.monotonic() - started_at, display_width)
                if time.monotonic() < state["hearts_until"]:
                    draw_heart(frame, (pet_center[0] + 62, pet_center[1] - 100), 24, PINK)

            draw_overlay(
                frame,
                state["enabled"],
                button_rect,
                active_gesture,
                bool(hand_landmarks_list),
            )
            cv2.imshow(WINDOW_NAME, frame)
            key = cv2.waitKey(1) & 0xFF
            if key in (ord("q"), 27):
                break
            if key in (ord("p"), ord("P")):
                state["enabled"] = not state["enabled"]
    finally:
        hands_model.close()
        camera.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    try:
        run()
    except RuntimeError as error:
        print(error)
        sys.exit(1)
