from nonebot.default_config import *
import importlib
from hoshino import log
from .__bot__ import *

# import configs
from . import deepchat
from . import groupmaster
from . import hourcall
from . import mikan
from . import priconne
from . import twitter
from . import mantra

# check correctness
RES_DIR = os.path.expanduser(RES_DIR)
assert RES_PROTOCOL in ('http', 'file', 'base64')

# load module configs
logger = log.new_logger('config')
for module in MODULES_ON:
    try:
        importlib.import_module('hoshino.config.' + module)
        logger.info(f'Succeeded to load config of "{module}"')
    except ModuleNotFoundError:
        logger.warning(f'Not found config of "{module}"')
