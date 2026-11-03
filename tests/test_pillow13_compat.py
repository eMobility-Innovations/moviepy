"""Current Pillow must preserve every painted pixel of multiline labels."""

import numpy as np
from PIL import Image, ImageDraw, ImageFont

from moviepy import TextClip


def test_multiline_label_preserves_descenders_and_stroke(util):
    text = "alpha\nbravo\ncharlie"
    font = ImageFont.truetype(util.FONT, 40)
    ascent, _ = font.getmetrics()
    reference = Image.new("RGB", (512, 512), "black")
    ImageDraw.Draw(reference).multiline_text(
        (3, ascent + 3), text, font=font, fill="white", spacing=12,
        stroke_width=3, stroke_fill="white", anchor="ls",
    )
    with TextClip(
        text=text, font=util.FONT, font_size=40, method="label",
        color="white", bg_color="black", stroke_width=3, stroke_color="white",
        interline=12, horizontal_align="left", vertical_align="top",
    ) as clip:
        frame = clip.get_frame(0)
        height, width = frame.shape[:2]
        _, _, right, bottom = reference.getbbox()
        assert right <= width and bottom <= height, "multiline text is clipped"
        np.testing.assert_array_equal(frame, np.asarray(reference)[:height, :width])
