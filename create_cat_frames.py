from pathlib import Path

from PIL import Image, ImageDraw


OUTPUT_DIR = Path(__file__).resolve().parent / "assets" / "fingercat" / "frames"
FRAME_SIZE = (420, 320)
ART_SCALE = 3

OUTLINE = "#70432f"
ORANGE = "#f6a84f"
LIGHT_ORANGE = "#ffd18a"
CREAM = "#fff4df"
PINK = "#f28da8"
EYE = "#563b34"


def scaled(point):
    return tuple(round(value * ART_SCALE) for value in point)


def bezier(points, steps=24):
    start, control_a, control_b, end = points
    result = []
    for index in range(steps + 1):
        t = index / steps
        inverse = 1 - t
        result.append((
            (inverse ** 3 * start[0] + 3 * inverse ** 2 * t * control_a[0]
             + 3 * inverse * t ** 2 * control_b[0] + t ** 3 * end[0]),
            (inverse ** 3 * start[1] + 3 * inverse ** 2 * t * control_a[1]
             + 3 * inverse * t ** 2 * control_b[1] + t ** 3 * end[1]),
        ))
    return result


def draw_curve(draw, points, color, width):
    draw.line([scaled(point) for point in bezier(points)], fill=color, width=width * ART_SCALE)
    radius = width * ART_SCALE // 2
    for point in (points[0], points[-1]):
        x, y = scaled(point)
        draw.ellipse((x - radius, y - radius, x + radius, y + radius), fill=color)


def draw_limb(draw, points, width, color=ORANGE):
    draw_curve(draw, points, OUTLINE, width + 8)
    draw_curve(draw, points, color, width)


def make_frame(frame_index):
    image = Image.new("RGBA", (FRAME_SIZE[0] * ART_SCALE, FRAME_SIZE[1] * ART_SCALE), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    gait = (-1, 1, 1, -1)[frame_index]
    tail_lift = (-8, 2, 9, 1)[frame_index]

    tail = [
        (128, 169),
        (72, 151 + tail_lift),
        (48, 109 + tail_lift),
        (74, 83 + tail_lift),
    ]
    draw_curve(draw, tail, OUTLINE, 29)
    draw_curve(draw, tail, ORANGE, 21)
    tail_tip = scaled((74, 83 + tail_lift))
    draw.ellipse((tail_tip[0] - 10 * ART_SCALE, tail_tip[1] - 10 * ART_SCALE,
                  tail_tip[0] + 10 * ART_SCALE, tail_tip[1] + 10 * ART_SCALE), fill=CREAM)

    rear_leg = [(282, 185), (293, 209 + gait * 3), (318, 220 + gait * 6), (337, 226 + gait * 6)]
    far_front_leg = [(190, 185), (195, 215 - gait * 5), (220, 230 - gait * 5), (239, 232 - gait * 5)]
    draw_limb(draw, rear_leg, 23)
    draw_limb(draw, far_front_leg, 22, LIGHT_ORANGE)

    draw = ImageDraw.Draw(image)
    bounds = tuple(value * ART_SCALE for value in (103, 123, 317, 231))
    draw.ellipse(bounds, fill=ORANGE, outline=OUTLINE, width=6 * ART_SCALE)
    belly = tuple(value * ART_SCALE for value in (166, 144, 278, 222))
    draw.ellipse(belly, fill=CREAM)
    hip_spot = tuple(value * ART_SCALE for value in (272, 145, 307, 177))
    draw.ellipse(hip_spot, fill=LIGHT_ORANGE)

    near_front_leg = [(207, 184), (218, 209 + gait * 5), (253, 214 + gait * 7), (275, 218 + gait * 7)]
    near_hind_leg = [(284, 184), (294, 206 - gait * 4), (322, 212 - gait * 6), (342, 220 - gait * 6)]
    draw_limb(draw, near_front_leg, 26, LIGHT_ORANGE)
    draw_limb(draw, near_hind_leg, 25)

    left_ear = [(116, 111), (108, 71), (144, 83), (158, 109)]
    right_ear = [(174, 98), (194, 54), (216, 85), (219, 117)]
    draw.polygon([scaled(point) for point in left_ear], fill=ORANGE)
    draw.line([scaled(point) for point in left_ear + [left_ear[0]]], fill=OUTLINE, width=5 * ART_SCALE, joint="curve")
    draw.polygon([scaled(point) for point in right_ear], fill=ORANGE)
    draw.line([scaled(point) for point in right_ear + [right_ear[0]]], fill=OUTLINE, width=5 * ART_SCALE, joint="curve")
    draw.polygon([scaled(point) for point in ((120, 101), (116, 82), (137, 91), (147, 105))], fill=PINK)
    draw.polygon([scaled(point) for point in ((184, 93), (195, 69), (209, 88), (212, 104))], fill=PINK)

    head = tuple(value * ART_SCALE for value in (103, 77, 230, 190))
    draw.ellipse(head, fill=ORANGE, outline=OUTLINE, width=6 * ART_SCALE)
    forehead = tuple(value * ART_SCALE for value in (126, 79, 179, 116))
    draw.ellipse(forehead, fill=LIGHT_ORANGE)

    for eye_x, eye_y, eye_w, eye_h in ((161, 123, 19, 27), (198, 132, 17, 24)):
        eye_box = tuple(value * ART_SCALE for value in
                        (eye_x - eye_w // 2, eye_y - eye_h // 2, eye_x + eye_w // 2, eye_y + eye_h // 2))
        draw.ellipse(eye_box, fill=EYE)
        shine = tuple(value * ART_SCALE for value in (eye_x - 5, eye_y - 9, eye_x + 2, eye_y - 2))
        draw.ellipse(shine, fill="#ffffff")
        small_shine = tuple(value * ART_SCALE for value in (eye_x + 3, eye_y + 4, eye_x + 7, eye_y + 8))
        draw.ellipse(small_shine, fill="#fff0c9")

    for cheek_x in (145, 208):
        cheek = tuple(value * ART_SCALE for value in (cheek_x - 9, 148, cheek_x + 9, 158))
        draw.ellipse(cheek, fill="#f58ea0")
    for stripe in (
        ((139, 91), (142, 98), (143, 103), (144, 108)),
        ((157, 84), (159, 91), (160, 96), (160, 102)),
        ((176, 87), (176, 93), (176, 98), (175, 104)),
    ):
        draw_curve(draw, stripe, "#b8753f", 3)

    draw.ellipse(tuple(value * ART_SCALE for value in (204, 143, 225, 160)), fill=CREAM)
    draw.ellipse(tuple(value * ART_SCALE for value in (218, 146, 228, 154)), fill=PINK)
    draw_curve(draw, [(221, 153), (219, 159), (215, 160), (212, 157)], OUTLINE, 2)
    draw_curve(draw, [(221, 153), (221, 159), (225, 160), (228, 157)], OUTLINE, 2)

    for whisker in (
        [(204, 145), (191, 137), (183, 136), (177, 134)],
        [(205, 151), (192, 151), (185, 153), (178, 155)],
        [(222, 145), (236, 137), (244, 137), (250, 134)],
        [(224, 151), (237, 151), (244, 153), (250, 156)],
    ):
        draw_curve(draw, whisker, "#9d6d58", 2)

    image = image.resize(FRAME_SIZE, Image.Resampling.LANCZOS)
    return image


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    for index in range(4):
        make_frame(index).save(OUTPUT_DIR / f"frame_{index:02d}.png", optimize=True)
    print(f"Created 4 transparent chibi cat frames in {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
