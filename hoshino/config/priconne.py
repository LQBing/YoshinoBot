from hoshino.util import get_environ


class arena:
    AUTH_KEY = get_environ('PCRDFANS_AUTH_KEY', r'')
