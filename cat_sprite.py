from pathlib import Path

import cv2
import numpy as np


DEFAULT_FRAMES_DIR = Path(__file__).resolve().parent / "assets" / "fingercat" / "frames"


class AnimatedCatSprite:
    def __init__(self, frames_dir=DEFAULT_FRAMES_DIR, frames_per_second=8):
        frame_paths = sorted(Path(frames_dir).glob("*.png"))
        if not frame_paths:
            raise RuntimeError(
                f"No transparent PNG sprite frames found in {frames_dir}. "
                "Run 'python create_cat_frames.py' to create the included chibi cat frames."
            )

        self.frames = []
        for frame_path in frame_paths:
            image = cv2.imread(str(frame_path), cv2.IMREAD_UNCHANGED)
            if image is None or image.ndim != 3 or image.shape[2] != 4:
                raise RuntimeError(f"Sprite frame must be a readable RGBA PNG: {frame_path}")
            if self.frames and image.shape != self.frames[0].shape:
                raise RuntimeError(f"All sprite frames must have the same dimensions: {frame_path}")
            self.frames.append(image)

        self.frames_per_second = frames_per_second
        self.width = self.frames[0].shape[1]
        self.height = self.frames[0].shape[0]

    def draw(self, frame, center, elapsed, display_width):
        sprite = self.frames[int(elapsed * self.frames_per_second) % len(self.frames)]
        display_height = max(1, round(display_width * self.height / self.width))
        interpolation = cv2.INTER_AREA if display_width < self.width else cv2.INTER_LINEAR
        sprite = cv2.resize(sprite, (display_width, display_height), interpolation=interpolation)

        center_x, center_y = center
        left = center_x - display_width // 2
        top = center_y - display_height // 2
        frame_height, frame_width = frame.shape[:2]
        x1, y1 = max(0, left), max(0, top)
        x2, y2 = min(frame_width, left + display_width), min(frame_height, top + display_height)
        if x1 >= x2 or y1 >= y2:
            return

        sprite_x1, sprite_y1 = x1 - left, y1 - top
        sprite_roi = sprite[sprite_y1:sprite_y1 + y2 - y1, sprite_x1:sprite_x1 + x2 - x1]
        foreground = sprite_roi[:, :, :3].astype(np.float32)
        alpha = sprite_roi[:, :, 3:4].astype(np.float32) / 255.0
        background = frame[y1:y2, x1:x2].astype(np.float32)
        frame[y1:y2, x1:x2] = (foreground * alpha + background * (1.0 - alpha)).astype(np.uint8)
