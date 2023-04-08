import re
from datetime import datetime

import peony
import pytz
from hoshino import util
from hoshino.typing import MessageSegment as ms


def format_time(time_str):
    dt = datetime.strptime(time_str, r"%a %b %d %H:%M:%S %z %Y")
    dt = dt.astimezone(pytz.timezone("Asia/Shanghai"))
    return f"{util.month_name(dt.month)}{util.date_name(dt.day)}・{util.time_name(dt.hour, dt.minute)}"


def format_tweet(tweet):
    name = tweet.user.name
    # avatar = tweet.user.get("profile_image_url_https", "https://abs.twimg.com/sticky/default_profile_images/default_profile_normal.png")
    # avatar = re.sub(r'_normal(\.(jpg|jpeg|png|gif|jfif|webp))$', r'_200x200\1', avatar, re.I)

    if peony.events.retweet(tweet):
        return f"@{name} 转推了\n>>>>>\n{format_tweet(tweet.retweeted_status)}"

    time = format_time(tweet.created_at)
    text = tweet.text
    media = tweet.get("extended_entities", {}).get("media", [])
    imgs = "".join([str(ms.image(m.media_url)) for m in media])
    msg = f"@{name}\n{time}\n\n{text}"
    if imgs:
        msg = f"{msg}\n{imgs}"

    if "quoted_status" in tweet:
        quoted_msg = format_tweet(tweet.quoted_status)
        msg = f"{quoted_msg}\n\n<<<<<\n{msg}"

    return msg
