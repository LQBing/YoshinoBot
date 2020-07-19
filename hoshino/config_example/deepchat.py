from hoshino.util import get_environ

# see https://github.com/peterli110/AutoRepeater
deepchat_api = get_environ('DEEPCHAT_API', "http://127.0.0.1:7777/message")
