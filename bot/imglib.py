from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from typing import TYPE_CHECKING

from PIL import Image, ImageDraw, ImageFont

from .utils import format_date

if TYPE_CHECKING:
    from collections.abc import Iterable


TEMPLATE_FILE = "img/airplane-cat_50.png"
FONT_FILE = "img/NotoSans_SemiCondensed-Bold.ttf"

airplane_cat = Image.open(TEMPLATE_FILE)
airplane_cat.load()

font = ImageFont.truetype(FONT_FILE, 96)


@dataclass(frozen=True)
class TextBox:
    text: str | Iterable[str]
    position: tuple[float, float]
    font: ImageFont.FreeTypeFont = font
    fill: tuple[int, int, int] = (255, 255, 255)
    stroke_fill: tuple[int, int, int] = (0, 0, 0)
    stroke_width: int = 8
    vertical_spacing: int = 8

    def draw(self, draw_obj: ImageDraw.ImageDraw) -> None:
        x, y = self.position
        text = self.text.splitlines() if isinstance(self.text, str) else self.text
        for line in text:
            left, top, right, bottom = self.font.getbbox(
                line, language="en", stroke_width=self.stroke_width
            )
            _width, height = right - left, bottom - top
            draw_obj.text(
                (x, y),
                line,
                font=self.font,
                anchor="ma",
                fill=self.fill,
                stroke_fill=self.stroke_fill,
                stroke_width=self.stroke_width,
                language="en",
            )
            y += height + self.vertical_spacing


def generate_image(date: datetime | None = None) -> Image.Image:
    if date is None:
        date = datetime.now(UTC)
    tomorrow = date + timedelta(days=1)

    if date.month == 4 and date.day == 1:  # April Fools' Day
        output: Image.Image = Image.open("img/dognose.png")
        output.load()
        img_width, img_height = output.size
        text1 = "Woah it's {} already?"
        text2 = "{}? Can't wait!"
        position1 = (img_width / 2, img_height * 0.17)
        position2 = (img_width / 2, img_height * 0.85)
    else:
        output = airplane_cat.copy()
        img_width, img_height = output.size
        text1 = "Damn it's {} already?"
        text2 = "{}? Fuck everything"
        position1 = (img_width / 2, img_height * 0.22)
        position2 = (img_width / 2, img_height * 0.75)

    draw = ImageDraw.Draw(output)
    textboxes = [
        TextBox(
            text=text1.format(format_date(date)),
            position=position1,
        ),
        TextBox(
            text=[
                "What's next?",
                text2.format(format_date(tomorrow)),
            ],
            position=position2,
        ),
    ]
    for textbox in textboxes:
        textbox.draw(draw)
    return output


if __name__ == "__main__":
    date = datetime.now(UTC)
    output = generate_image()
    output.save("output_today.png")
    output = generate_image(date.replace(month=4, day=1))
    output.save("output_april_1st.png")
