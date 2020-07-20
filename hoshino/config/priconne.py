from hoshino.util import get_environ, get_bool_environ


class arena:
    AUTH_KEY = get_environ('PCRDFANS_AUTH_KEY')


class gacha:
    ENABLE_SILENCE = get_bool_environ('ENABLE_SILENCE', True)
