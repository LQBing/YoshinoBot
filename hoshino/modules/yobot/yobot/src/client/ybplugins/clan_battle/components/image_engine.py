from PIL import Image, ImageDraw, ImageFont
import os
from typing import Tuple, List, Optional, Dict, Set
from pathlib import Path
import random
import httpx
import asyncio
import logging

_logger = logging.getLogger(__name__)

FILE_PATH = os.path.dirname(__file__)
FONTS_PATH = os.path.join(FILE_PATH, "fonts")
FONTS = os.path.join(FONTS_PATH, "msyh.ttf")
USER_HEADERS_PATH = Path(__file__).parent.joinpath("../../../yobot_data/user_profile")
BOSS_ICON_PATH = Path(__file__).parent.joinpath("../../../public/libs/yocool@final/princessadventure/boss_icon")
if not USER_HEADERS_PATH.is_dir():
    USER_HEADERS_PATH.mkdir()

# CHIPS_COLOR_LIST = [(229, 115, 115), (186, 104, 200), (149, 177, 205), (100, 181, 246), (77, 182, 172), (220, 231, 177)]
CHIPS_COLOR_DICT = {"预约": (179, 229, 252), "挑战": (220, 237, 200), "挂树": (255, 205, 210)}

glovar_missing_user_id: Set[int] = set()


def get_font_image(text: str, size: int, color: Tuple[int, int, int] = (0, 0, 0)) -> Image.Image:
    background = Image.new("RGBA", (len(text) * size, 100), (255, 255, 255, 0))
    background_draw = ImageDraw.Draw(background)
    image_font = ImageFont.truetype(FONTS, size)
    background_draw.text((0, 0), text=text, font=image_font, fill=color)
    return background.crop(background.getbbox())


def center(source_image: Image.Image, target_image: Image.Image) -> Tuple[int, int]:
    result = [0, 0]
    target_image_box = target_image.getbbox()
    if target_image_box is None:
        return (0, 0)
    boxes = (source_image.size, target_image_box[2:])
    for i in range(2):
        result[i] = (boxes[0][i] - boxes[1][i]) / 2
    return tuple(map(lambda i: round(i), result))


def round_corner(image: Image.Image, radius: Optional[int] = None) -> Image.Image:
    if radius is None:
        size = image.height
    else:
        size = radius * 2

    circle_bg = Image.new("L", (size * 5, size * 5), 0)
    circle_draw = ImageDraw.Draw(circle_bg)
    circle_draw.ellipse((0, 0, size * 5, size * 5), 255)
    circle_bg = circle_bg.resize((size, size))

    if radius is None:
        circle_split_cursor_x = round(circle_bg.size[0] / 2)
        circle_split = (circle_bg.crop((0, 0, circle_split_cursor_x, size)), circle_bg.crop((circle_split_cursor_x, 0, size, size)))

        mask = Image.new("L", image.size, 255)
        mask.paste(circle_split[0], (0, 0))
        mask.paste(circle_split[1], (image.width - circle_split[1].width, 0))
    else:
        circle_split = (
            circle_bg.crop((0, 0, radius, radius)),
            circle_bg.crop((radius, 0, radius * 2, radius)),
            circle_bg.crop((0, radius, radius, radius * 2)),
            circle_bg.crop((radius, radius, radius * 2, radius * 2)),
        )
        mask = Image.new("L", image.size, 255)
        mask.paste(circle_split[0], (0, 0))
        mask.paste(circle_split[1], (image.width - radius, 0))
        mask.paste(circle_split[2], (0, image.height - radius))
        mask.paste(circle_split[3], (image.width - radius, image.height - radius))

    mask_paste_bg = Image.new("RGBA", image.size, (255, 255, 255, 0))

    return Image.composite(image, mask_paste_bg, mask)


def user_chips(head_icon: Image.Image, user_name: str) -> Image.Image:
    head_icon = head_icon.resize((20, 20))
    head_icon = round_corner(head_icon)

    # background_color = tuple(random.randint(10, 240) for i in range(3))
    # background_color = (228, 228, 228)
    background_color = (189, 189, 189)
    is_white_text = True if ((background_color[0] * 0.299 + background_color[1] * 0.587 + background_color[2] * 0.114) / 255) < 0.5 else False

    user_name_image = get_font_image(user_name, 20, (255, 255, 255) if is_white_text else (0, 0, 0))

    background = Image.new("RGBA", (15 + head_icon.width + user_name_image.width, 24), background_color)
    background.alpha_composite(head_icon, (5, 2))
    background.alpha_composite(user_name_image, (30, center(background, user_name_image)[1]))

    return round_corner(background)


def chips_list(chips_array: Dict[str, str] = {}, text: str = "内容", background_color: Tuple[int, int, int] = (255, 255, 255)) -> Image.Image:
    global glovar_missing_user_id
    CHIPS_LIST_WIDTH = 340
    background = Image.new("RGBA", (CHIPS_LIST_WIDTH, 350), background_color)
    is_white_text = True if ((background_color[0] * 0.299 + background_color[1] * 0.587 + background_color[2] * 0.114) / 255) < 0.5 else False
    text_image = get_font_image("\n".join([i for i in text]), 24, (255, 255, 255) if is_white_text else (0, 0, 0))
    if not chips_array:
        background = background.crop((0, 0, CHIPS_LIST_WIDTH, 64))
        background.alpha_composite(text_image, (5, center(background, text_image)[1]))
        text_image = get_font_image(f"暂无{text}", 28, (255, 255, 255) if is_white_text else (0, 0, 0))
        background.alpha_composite(text_image, center(background, text_image))
        return round_corner(background, 5)

    chips_image_list = []
    for i, j in chips_array.items():
        user_profile_path = USER_HEADERS_PATH.joinpath(i + ".jpg")
        if not user_profile_path.is_file():
            user_profile_image = Image.new("RGBA", (20, 20), (255, 255, 255, 0))
            glovar_missing_user_id.add(int(i))
        else:
            user_profile_image = Image.open(USER_HEADERS_PATH.joinpath(i + ".jpg"), "r")
        chips_image_list.append(user_chips(user_profile_image, j))
    chips_image_list.sort(key=lambda i: i.width)
    this_width = 34
    this_height = 5
    for this_chip in chips_image_list:
        if this_width + this_chip.width <= CHIPS_LIST_WIDTH:
            background.alpha_composite(this_chip, (this_width, this_height))
            this_width += this_chip.width + 5
        else:
            this_height += 29
            this_width = 34
            background.alpha_composite(this_chip, (this_width, this_height))
            this_width += this_chip.width
    if this_height + 34 <= 64:
        background = background.crop((0, 0, CHIPS_LIST_WIDTH, 64))
    else:
        background = background.crop((0, 0, CHIPS_LIST_WIDTH, this_height + 34))
    background.alpha_composite(text_image, (5, center(background, text_image)[1]))
    return round_corner(background, 5)


def get_process_image(finish_challenge_count: int, half_challenge_list: Dict[str, str]):
    overall_image = Image.new("RGBA", (498, 500), (255, 255, 255, 0))
    full_challenge_text = get_font_image(f"完整刀", 24)
    full_challenge_count_text = get_font_image(str(finish_challenge_count), 24, (255, 0, 0))
    overall_image.alpha_composite(full_challenge_text, (round((148 - full_challenge_text.width) / 2), 15))
    overall_image.alpha_composite(full_challenge_count_text, (round((148 - full_challenge_count_text.width) / 2), 49))
    chips_list_image = chips_list(half_challenge_list, "补偿", (237, 231, 246))
    overall_image.alpha_composite(chips_list_image, (148, 10))
    return overall_image.crop((0, 0, 498, chips_list_image.height + 20))


class BossStatusImageCore:
    def __init__(
        self,
        cyle: int,
        boss_round: int,
        current_hp: int,
        max_hp: int,
        name: str,
        boss_icon_id: str,
        extra_chips_array: Dict[str, Dict[str, str]],
    ) -> None:
        self.current_hp = current_hp
        self.max_hp = max_hp
        self.cyle = cyle
        self.round = boss_round
        self.name = name
        self.boss_icon_id = boss_icon_id
        self.extra_chips_array = extra_chips_array

    def hp_percent_image(self) -> Image.Image:
        HP_PERCENT_IMAGE_SIZE = (340, 24)
        background = Image.new("RGBA", HP_PERCENT_IMAGE_SIZE, (200, 200, 200))
        background_draw = ImageDraw.Draw(background, "RGBA")
        percent_pixel_cursor_x = round(self.current_hp / self.max_hp * HP_PERCENT_IMAGE_SIZE[0])
        background_draw.rectangle((0, 0, percent_pixel_cursor_x, HP_PERCENT_IMAGE_SIZE[1]), (255, 0, 0))

        text_str = f"{self.current_hp} / {self.max_hp}"
        text_image_white = get_font_image(text_str, 20, (255, 255, 255))
        text_image_black = get_font_image(text_str, 20)
        text_paste_center_start_cursor = center(background, text_image_white)
        text_image = Image.new("RGBA", text_image_white.size)
        seek_in_text_image = percent_pixel_cursor_x - text_paste_center_start_cursor[0] + 1
        if seek_in_text_image <= 0:
            text_image = text_image_black
        elif seek_in_text_image >= text_image_white.width:
            text_image = text_image_white
        else:
            text_image.alpha_composite(
                text_image_white.crop((0, 0, seek_in_text_image, text_image_white.size[1])),
                dest=(0, 0),
            )
            text_image.alpha_composite(
                text_image_black.crop((seek_in_text_image, 0, *text_image_black.size)),
                dest=(seek_in_text_image, 0),
            )
        background.alpha_composite(text_image, text_paste_center_start_cursor)

        return round_corner(background)

    def cyle_round_image(self) -> Image.Image:
        text_str = f"{self.cyle} 阶段， {self.round} 周目"
        text_image = get_font_image(text_str, 20, (255, 255, 255))
        background = Image.new("RGBA", (text_image.width + 24, 24), (3, 169, 244, 255))
        background.alpha_composite(text_image, center(background, text_image))
        return round_corner(background)

    def generate(self, background_color: Tuple[int, int, int] = (255, 255, 255)) -> Image.Image:
        BOSS_HEADER_SIZE = 128

        background = Image.new("RGBA", (498, 1000), background_color)

        boss_name_image = get_font_image(self.name, 24)
        background.alpha_composite(boss_name_image, (BOSS_HEADER_SIZE + 20, 10))
        background.alpha_composite(self.cyle_round_image(), (BOSS_HEADER_SIZE + 30 + boss_name_image.width, 10))
        background.alpha_composite(self.hp_percent_image(), (BOSS_HEADER_SIZE + 20, 44))

        if not BOSS_ICON_PATH.joinpath(self.boss_icon_id + ".webp").is_file():
            boss_icon = Image.new("RGBA", (128, 128), (255, 255, 255, 0))
        else:
            boss_icon = Image.open(BOSS_ICON_PATH.joinpath(self.boss_icon_id + ".webp"), "r")

        boss_icon = boss_icon.resize((128, 128))
        boss_icon = round_corner(boss_icon, 10)
        background.alpha_composite(boss_icon, (10, 10))

        current_chips_height = 78
        for this_chips_list in self.extra_chips_array:
            chips_background_color = (240, 240, 240)
            if this_chips_list in CHIPS_COLOR_DICT:
                chips_background_color = CHIPS_COLOR_DICT[this_chips_list]
            chips_list_image = chips_list(self.extra_chips_array[this_chips_list], this_chips_list, chips_background_color)
            background.alpha_composite(chips_list_image, (BOSS_HEADER_SIZE + 20, current_chips_height))
            current_chips_height += chips_list_image.height + 10

        return background.crop((0, 0, background.width, current_chips_height))


def generate_combind_boss_state_image(boss_state: List[BossStatusImageCore], before: Optional[Image.Image] = None, after: Optional[Image.Image] = None) -> Image.Image:
    background = Image.new("RGBA", (498, 3000), (255, 255, 255))
    current_y_cursor = 0
    format_color_flag = False

    if before:
        background.paste(before, (0, 0))
        current_y_cursor = before.height
        format_color_flag = True

    for this_image in boss_state:
        this_image = this_image.generate((249, 251, 231) if format_color_flag else (255, 255, 255))
        background.paste(this_image, (0, current_y_cursor))
        current_y_cursor += this_image.height
        format_color_flag = not format_color_flag

    if after:
        background.paste(after, (0, current_y_cursor))
        current_y_cursor += after.height

    return background.crop((0, 0, background.width, current_y_cursor))


async def download_pic(url: str, proxies: Optional[str] = None, file_name="") -> Optional[Path]:
    image_path = USER_HEADERS_PATH.joinpath(file_name)
    client = httpx.AsyncClient(proxies=proxies, timeout=5)
    try:
        async with client.stream(method="GET", url=url, timeout=15) as response:  # type: ignore # params={"proxies": [proxies]}
            if response.status_code != 200:
                raise ValueError(f"Image respond status code error: {response.status_code}")
            with open(image_path, "wb") as f:
                async for chunk in response.aiter_bytes():
                    f.write(chunk)
    except Exception:
        return None
    finally:
        await client.aclose()
    return image_path


async def download_user_profile_image(user_id_list: List[int]) -> None:
    task_list = []
    for this_user_id in user_id_list:
        task_list.append(download_pic(f"http://q1.qlogo.cn/g?b=qq&nk={this_user_id}&s=1", file_name=f"{this_user_id}.jpg"))
    await asyncio.gather(*task_list)


async def download_missing_user_profile() -> None:
    global glovar_missing_user_id
    if not glovar_missing_user_id:
        return
    await download_user_profile_image(list(glovar_missing_user_id))
    glovar_missing_user_id = set()
