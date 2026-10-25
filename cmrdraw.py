import math
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path

import cv2
import mediapipe as mp
import numpy as np


CAMERA_INDEX = 0
MAX_HANDS = 2
MIN_DETECTION_CONFIDENCE = 0.65
MIN_TRACKING_CONFIDENCE = 0.55
LANDMARK_SMOOTHING = 0.4
GESTURE_STABLE_FRAMES = 3
OPEN_PALM_RELEASE_FRAMES = 8
FINGER_EXTENSION_MARGIN = 0.015
PINCH_DISTANCE_RATIO = 0.35
MAX_STROKE_JUMP_RATIO = 0.12
MAX_STROKES = 100
HEADER_HEIGHT = 70
SIDEBAR_WIDTH = 130
BRUSH_MIN = 1
BRUSH_MAX = 50
ZOOM_MIN = 0.5
ZOOM_MAX = 3.0

COLORS = [
    (0, 0, 255),
    (255, 0, 255),
    (255, 20, 147),
    (255, 105, 180),
    (255, 182, 193),
    (255, 192, 203),
    (0, 255, 0),
    (255, 255, 0),
    (0, 255, 255),
    (255, 255, 255),
    (0, 0, 0),
]
CONTROL_ACTIONS = (
    "CLEAR",
    "UNDO",
    "REDO",
    "BRUSH -",
    "BRUSH +",
    "ERASER",
    "ZOOM -",
    "ZOOM +",
    "PAUSE",
    "SAVE",
)
SAVE_PATH = Path(__file__).resolve().parent / "love_drawing.png"


@dataclass
class HandObservation:
    side: str
    landmarks: object
    points: list


@dataclass
class Stroke:
    color: tuple
    size: int
    erasing: bool
    points: list = field(default_factory=list)


class HandTracker:
    def __init__(self):
        self.hands_model = mp.solutions.hands.Hands(
            static_image_mode=False,
            max_num_hands=MAX_HANDS,
            model_complexity=0,
            min_detection_confidence=MIN_DETECTION_CONFIDENCE,
            min_tracking_confidence=MIN_TRACKING_CONFIDENCE,
        )
        self.smoothed_points = {}

    def process(self, frame):
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        rgb_frame.flags.writeable = False
        results = self.hands_model.process(rgb_frame)
        observations = []

        landmark_sets = results.multi_hand_landmarks or []
        handedness_sets = results.multi_handedness or []
        visible_sides = set()

        for index, landmarks in enumerate(landmark_sets):
            side = "hand"
            if index < len(handedness_sets) and handedness_sets[index].classification:
                side = handedness_sets[index].classification[0].label.lower()
            visible_sides.add(side)

            raw_points = [
                (landmark.x, landmark.y, landmark.z)
                for landmark in landmarks.landmark
            ]
            previous = self.smoothed_points.get(side)
            if previous is None or len(previous) != len(raw_points):
                smoothed = raw_points
            else:
                smoothed = [
                    tuple(
                        old_value + LANDMARK_SMOOTHING * (new_value - old_value)
                        for old_value, new_value in zip(old_point, new_point)
                    )
                    for old_point, new_point in zip(previous, raw_points)
                ]
            self.smoothed_points[side] = smoothed
            observations.append(HandObservation(side, landmarks, smoothed))

        for side in list(self.smoothed_points):
            if side not in visible_sides:
                del self.smoothed_points[side]

        return observations

    def close(self):
        self.hands_model.close()


class GestureRecognizer:
    def __init__(self):
        self.candidates = {}
        self.candidate_counts = {}
        self.stable_gestures = {}

    @staticmethod
    def classify(landmarks):
        points = landmarks.landmark
        finger_extended = [
            points[tip].y < points[pip].y - FINGER_EXTENSION_MARGIN
            for tip, pip in ((8, 6), (12, 10), (16, 14), (20, 18))
        ]
        index, middle, ring, pinky = finger_extended

        palm_width = math.hypot(
            points[5].x - points[17].x,
            points[5].y - points[17].y,
        )
        pinch_distance = math.hypot(
            points[4].x - points[8].x,
            points[4].y - points[8].y,
        )
        if palm_width > 0 and pinch_distance < palm_width * PINCH_DISTANCE_RATIO:
            return "PINCH"
        if index and middle and ring and pinky:
            return "OPEN PALM"
        if index and middle and not ring and not pinky:
            return "TWO FINGERS"
        if index and not middle and not ring and not pinky:
            return "DRAW"
        if not any(finger_extended):
            return "FIST"
        return "OTHER"

    def update(self, side, gesture):
        if self.candidates.get(side) == gesture:
            self.candidate_counts[side] = self.candidate_counts.get(side, 0) + 1
        else:
            self.candidates[side] = gesture
            self.candidate_counts[side] = 1

        if self.candidate_counts[side] < GESTURE_STABLE_FRAMES:
            return self.stable_gestures.get(side), False

        previous = self.stable_gestures.get(side)
        self.stable_gestures[side] = gesture
        return gesture, previous != gesture

    def remove(self, side):
        self.candidates.pop(side, None)
        self.candidate_counts.pop(side, None)
        self.stable_gestures.pop(side, None)


class DrawingCanvas:
    def __init__(self, height, width):
        self.image = np.zeros((height, width, 3), dtype=np.uint8)
        self.strokes = []
        self.redo_strokes = []

    def start_stroke(self, point, color, size, erasing):
        stroke = Stroke(color, size, erasing, [point])
        self.strokes.append(stroke)
        self.redo_strokes.clear()
        if len(self.strokes) > MAX_STROKES:
            del self.strokes[0]
        self._draw_dot(point, stroke)
        return stroke

    def add_point(self, stroke, point):
        previous = stroke.points[-1]
        distance = math.hypot(point[0] - previous[0], point[1] - previous[1])
        max_jump = math.hypot(self.image.shape[1], self.image.shape[0]) * MAX_STROKE_JUMP_RATIO
        if distance > max_jump:
            return False
        stroke.points.append(point)
        color = (0, 0, 0) if stroke.erasing else stroke.color
        cv2.line(self.image, previous, point, color, stroke.size * 2, cv2.LINE_AA)
        return True

    def undo(self):
        if self.strokes:
            self.redo_strokes.append(self.strokes.pop())
            self.redraw()

    def redo(self):
        if self.redo_strokes:
            self.strokes.append(self.redo_strokes.pop())
            self.redraw()

    def clear(self):
        self.strokes.clear()
        self.redo_strokes.clear()
        self.image.fill(0)

    def redraw(self):
        self.image.fill(0)
        for stroke in self.strokes:
            self._draw_dot(stroke.points[0], stroke)
            color = (0, 0, 0) if stroke.erasing else stroke.color
            for start, end in zip(stroke.points, stroke.points[1:]):
                cv2.line(
                    self.image,
                    start,
                    end,
                    color,
                    stroke.size * 2,
                    cv2.LINE_AA,
                )

    def _draw_dot(self, point, stroke):
        color = (0, 0, 0) if stroke.erasing else stroke.color
        cv2.circle(self.image, point, stroke.size, color, -1, cv2.LINE_AA)


def save_drawing(drawing):
    if not cv2.imwrite(str(SAVE_PATH), drawing.image):
        print(f"Could not save drawing to: {SAVE_PATH}")
        return f"Save failed: {SAVE_PATH.name}"
    print(f"Drawing saved to: {SAVE_PATH}")
    return f"Saved: {SAVE_PATH.name}"


def control_button_bounds(index, frame_height):
    button_height = min(40, max(24, (frame_height - HEADER_HEIGHT - 24) // len(CONTROL_ACTIONS) - 4))
    gap = 4
    top = HEADER_HEIGHT + 8 + index * (button_height + gap)
    return top, top + button_height


def control_at(x, y, frame_width, frame_height):
    if x < frame_width - SIDEBAR_WIDTH:
        return None
    for index, action in enumerate(CONTROL_ACTIONS):
        top, bottom = control_button_bounds(index, frame_height)
        if top <= y <= bottom:
            return action
    return None


def color_at(x, y, frame_width):
    if y >= HEADER_HEIGHT or x >= frame_width - SIDEBAR_WIDTH:
        return None
    palette_width = frame_width - SIDEBAR_WIDTH
    return min(int(x / (palette_width / len(COLORS))), len(COLORS) - 1)


def draw_interface(
    frame,
    current_color,
    color_index,
    brush_size,
    erasing,
    paused,
    status,
    pinch_cursor=None,
    hovered_action=None,
    hovered_color=None,
):
    height, width, _ = frame.shape
    sidebar_x = width - SIDEBAR_WIDTH
    cv2.rectangle(frame, (0, 0), (width, HEADER_HEIGHT), (30, 30, 30), -1)

    available_width = max(1, width - SIDEBAR_WIDTH)
    button_width = available_width / len(COLORS)
    for index, color in enumerate(COLORS):
        left = int(index * button_width)
        right = int((index + 1) * button_width)
        cv2.rectangle(frame, (left, 0), (right, HEADER_HEIGHT), color, -1)
        if index == color_index or index == hovered_color:
            outline = (0, 255, 255) if index == hovered_color else (255, 255, 255)
            thickness = 3 if index == hovered_color else 2
            cv2.rectangle(
                frame,
                (left + 2, 2),
                (right - 2, HEADER_HEIGHT - 2),
                outline,
                thickness,
            )
        cv2.putText(
            frame,
            str(index + 1),
            (left + 7, HEADER_HEIGHT - 12),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.45,
            (0, 0, 0) if index in (4, 5, 9) else (255, 255, 255),
            1,
        )

    cv2.rectangle(frame, (sidebar_x, HEADER_HEIGHT), (width, height), (40, 40, 40), -1)
    for index, action in enumerate(CONTROL_ACTIONS):
        top, bottom = control_button_bounds(index, height)
        if top >= height:
            break
        fill = (70, 80, 90)
        if action == "ERASER" and erasing:
            fill = (40, 100, 200)
        elif action == "PAUSE" and paused:
            fill = (40, 100, 200)
        if action == hovered_action:
            fill = (90, 125, 150)
        cv2.rectangle(frame, (sidebar_x + 6, top), (width - 6, bottom), fill, -1)
        cv2.putText(
            frame,
            action,
            (sidebar_x + 10, top + min(25, bottom - top - 6)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.38,
            (255, 255, 255),
            1,
        )

    gesture_label = "PAUSED" if paused else "DRAW / GESTURE"
    cv2.putText(frame, gesture_label, (12, height - 48),
                cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 255, 255), 2)
    mode_label = f"Brush: {brush_size} | {'ERASER' if erasing else 'PEN'}"
    cv2.putText(frame, mode_label, (12, height - 25),
                cv2.FONT_HERSHEY_SIMPLEX, 0.48, (255, 255, 255), 1)
    if status:
        cv2.putText(frame, status, (12, HEADER_HEIGHT + 25),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
    cv2.putText(frame, "Index: draw | Fist: stop | Pinch: select",
                (12, HEADER_HEIGHT + 48), cv2.FONT_HERSHEY_SIMPLEX,
                0.43, (255, 255, 255), 1)
    cv2.putText(frame, "Two fingers: undo | Open palm: pause",
                (12, HEADER_HEIGHT + 68), cv2.FONT_HERSHEY_SIMPLEX,
                0.43, (255, 255, 255), 1)
    cv2.putText(frame, "Pinch over a button to select | Q: quit",
                (12, HEADER_HEIGHT + 88), cv2.FONT_HERSHEY_SIMPLEX,
                0.43, (255, 255, 255), 1)
    cv2.putText(frame, f"Color {color_index + 1}", (12, HEADER_HEIGHT + 110),
                cv2.FONT_HERSHEY_SIMPLEX, 0.43, (255, 255, 255), 1)
    cv2.rectangle(frame, (78, HEADER_HEIGHT + 97), (98, HEADER_HEIGHT + 116),
                  current_color, -1)
    cv2.rectangle(frame, (78, HEADER_HEIGHT + 97), (98, HEADER_HEIGHT + 116),
                  (255, 255, 255), 1)
    if pinch_cursor is not None:
        cv2.circle(frame, pinch_cursor, 12, (0, 255, 255), 2)
        cv2.circle(frame, pinch_cursor, 3, (0, 255, 255), -1)


def apply_control(action, drawing, state):
    if action == "CLEAR":
        drawing.clear()
    elif action == "UNDO":
        drawing.undo()
    elif action == "REDO":
        drawing.redo()
    elif action == "ERASER":
        state["erasing"] = not state["erasing"]
    elif action == "BRUSH -":
        state["brush_size"] = max(state["brush_size"] - 2, BRUSH_MIN)
    elif action == "BRUSH +":
        state["brush_size"] = min(state["brush_size"] + 2, BRUSH_MAX)
    elif action == "ZOOM -":
        state["zoom"] = max(state["zoom"] - 0.1, ZOOM_MIN)
    elif action == "ZOOM +":
        state["zoom"] = min(state["zoom"] + 0.1, ZOOM_MAX)
    elif action == "PAUSE":
        state["paused"] = not state["paused"]
    elif action == "SAVE":
        state["status"] = save_drawing(drawing)
        state["status_until"] = time.monotonic() + 3
        return

    messages = {
        "CLEAR": "Canvas cleared",
        "UNDO": "Undo",
        "REDO": "Redo",
        "BRUSH -": f"Brush size: {state['brush_size']}",
        "BRUSH +": f"Brush size: {state['brush_size']}",
        "ERASER": "Eraser on" if state["erasing"] else "Eraser off",
        "ZOOM -": f"Zoom: {state['zoom']:.1f}x",
        "ZOOM +": f"Zoom: {state['zoom']:.1f}x",
        "PAUSE": "Drawing paused" if state["paused"] else "Drawing resumed",
    }
    state["status"] = messages[action]
    state["status_until"] = time.monotonic() + 2


def run():
    tracker = HandTracker()
    camera = cv2.VideoCapture(CAMERA_INDEX)
    if not camera.isOpened():
        camera.release()
        tracker.close()
        raise RuntimeError(f"Could not open camera {CAMERA_INDEX}. Check that it is connected and available.")

    camera.set(cv2.CAP_PROP_FRAME_WIDTH, 960)
    camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 540)
    camera.set(cv2.CAP_PROP_BUFFERSIZE, 1)

    recognizer = GestureRecognizer()
    drawing = None
    previous_points = {}
    active_strokes = {}
    state = {
        "color_index": 0,
        "brush_size": 5,
        "erasing": False,
        "paused": False,
        "zoom": 1.0,
        "status": "",
        "status_until": 0.0,
        "open_palm_active": False,
        "open_palm_release_frames": 0,
    }

    try:
        failed_frames = 0
        while True:
            success, frame = camera.read()
            if not success:
                failed_frames += 1
                if failed_frames >= 3:
                    print("Camera stopped returning frames; drawing has been paused.")
                    break
                continue
            failed_frames = 0

            frame = cv2.flip(frame, 1)
            height, width, _ = frame.shape
            if drawing is None:
                drawing = DrawingCanvas(height, width)

            if state["zoom"] != 1.0:
                transform = np.array([
                    [state["zoom"], 0, (1 - state["zoom"]) * width / 2],
                    [0, state["zoom"], (1 - state["zoom"]) * height / 2],
                ], dtype=np.float32)
                frame = cv2.warpAffine(frame, transform, (width, height))

            observations = tracker.process(frame)
            visible_sides = {observation.side for observation in observations}
            tracked_sides = set(previous_points) | set(recognizer.stable_gestures)
            for side in tracked_sides:
                if side not in visible_sides:
                    previous_points.pop(side, None)
                    active_strokes.pop(side, None)
                    recognizer.remove(side)

            draw_events = []
            pinch_events = []
            pinch_cursors = []
            open_sides = []
            for observation in observations:
                raw_gesture = recognizer.classify(observation.landmarks)
                stable_gesture, changed = recognizer.update(observation.side, raw_gesture)
                index_x, index_y = observation.points[8][:2]
                point = (int(index_x * width), int(index_y * height))
                pinch_x = (observation.points[4][0] + index_x) / 2
                pinch_y = (observation.points[4][1] + index_y) / 2
                cursor = (int(pinch_x * width), int(pinch_y * height))
                pinch_cursors.append(cursor)

                if raw_gesture != "DRAW" or changed:
                    previous_points.pop(observation.side, None)
                    active_strokes.pop(observation.side, None)
                if stable_gesture == "OPEN PALM":
                    open_sides.append(observation.side)
                if changed and stable_gesture == "TWO FINGERS":
                    draw_events.append("UNDO")
                if changed and stable_gesture == "PINCH":
                    pinch_events.append(cursor)

                if raw_gesture == "DRAW" and stable_gesture == "DRAW" and not state["paused"]:
                    if HEADER_HEIGHT < point[1] < height - 105 and point[0] < width - SIDEBAR_WIDTH:
                        if observation.side not in previous_points:
                            active_strokes[observation.side] = drawing.start_stroke(
                                point,
                                COLORS[state["color_index"]],
                                state["brush_size"],
                                state["erasing"],
                            )
                        elif not drawing.add_point(active_strokes[observation.side], point):
                            active_strokes[observation.side] = drawing.start_stroke(
                                point,
                                COLORS[state["color_index"]],
                                state["brush_size"],
                                state["erasing"],
                            )
                        previous_points[observation.side] = point
                    else:
                        previous_points.pop(observation.side, None)
                        active_strokes.pop(observation.side, None)
                else:
                    previous_points.pop(observation.side, None)
                    active_strokes.pop(observation.side, None)

                mp.solutions.drawing_utils.draw_landmarks(
                    frame,
                    observation.landmarks,
                    mp.solutions.hands.HAND_CONNECTIONS,
                )
                cv2.circle(frame, point, 8, (0, 255, 255), 2)
                cv2.putText(frame, observation.side.title(), (point[0] + 8, point[1] - 8),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 255, 255), 1)

            if open_sides and not state["open_palm_active"]:
                state["paused"] = not state["paused"]
                previous_points.clear()
                active_strokes.clear()
                state["status"] = "Drawing paused" if state["paused"] else "Drawing resumed"
                state["status_until"] = time.monotonic() + 2
            if open_sides:
                state["open_palm_active"] = True
                state["open_palm_release_frames"] = 0
            elif any(
                recognizer.stable_gestures.get(observation.side) not in (None, "OPEN PALM")
                for observation in observations
            ):
                state["open_palm_active"] = False
                state["open_palm_release_frames"] = 0
            elif state["open_palm_active"]:
                state["open_palm_release_frames"] += 1
                if state["open_palm_release_frames"] >= OPEN_PALM_RELEASE_FRAMES:
                    state["open_palm_active"] = False

            if draw_events:
                drawing.undo()
                previous_points.clear()
                active_strokes.clear()
            if pinch_events:
                cursor_x, cursor_y = pinch_events[0]
                selected_color = color_at(cursor_x, cursor_y, width)
                if selected_color is not None:
                    state["color_index"] = selected_color
                    state["status"] = f"Color {selected_color + 1} selected"
                    state["status_until"] = time.monotonic() + 2
                else:
                    action = control_at(cursor_x, cursor_y, width, height)
                    if action is not None:
                        apply_control(action, drawing, state)
                        previous_points.clear()
                        active_strokes.clear()

            status = state["status"] if time.monotonic() < state["status_until"] else ""
            pinch_cursor = pinch_cursors[0] if pinch_cursors else None
            hovered_action = (
                control_at(pinch_cursor[0], pinch_cursor[1], width, height)
                if pinch_cursor is not None
                else None
            )
            hovered_color = (
                color_at(pinch_cursor[0], pinch_cursor[1], width)
                if pinch_cursor is not None
                else None
            )
            draw_interface(
                frame,
                COLORS[state["color_index"]],
                state["color_index"],
                state["brush_size"],
                state["erasing"],
                state["paused"],
                status,
                pinch_cursor,
                hovered_action,
                hovered_color,
            )
            frame = cv2.addWeighted(frame, 0.7, drawing.image, 0.3, 0)
            cv2.imshow("Love Drawing App - Hand Gesture", frame)

            key = cv2.waitKey(1) & 0xFF
            if key == ord("q"):
                break
            if key in (ord("+"), ord("=")):
                state["zoom"] = min(state["zoom"] + 0.1, ZOOM_MAX)
            elif key in (ord("-"), ord("_")):
                state["zoom"] = max(state["zoom"] - 0.1, ZOOM_MIN)
            elif key in (ord("s"), ord("S")):
                state["status"] = save_drawing(drawing)
                state["status_until"] = time.monotonic() + 3
            elif key == ord("["):
                state["brush_size"] = max(state["brush_size"] - 1, BRUSH_MIN)
            elif key == ord("]"):
                state["brush_size"] = min(state["brush_size"] + 1, BRUSH_MAX)
            elif key in (ord("e"), ord("E")):
                state["erasing"] = not state["erasing"]
            elif key == 26:
                drawing.undo()
                previous_points.clear()
                active_strokes.clear()
            elif key == 25:
                drawing.redo()
                previous_points.clear()
                active_strokes.clear()
            elif key in (ord("p"), ord("P")):
                state["paused"] = not state["paused"]
                previous_points.clear()
                active_strokes.clear()
    finally:
        tracker.close()
        camera.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    try:
        run()
    except RuntimeError as error:
        print(error)
        sys.exit(1)
