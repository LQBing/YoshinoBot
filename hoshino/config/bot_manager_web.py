from hoshino.util import get_environ
from .__bot__ import HOST, PORT

ICP_CONTENT = get_environ('ICP_CONTENT')
DOMAIN_URL = get_environ('DOMAIN_URL', f"http://{HOST}:{PORT}")
PASSWORD = get_environ('BOT_MANAGER_WEB_PASSWORD', 'l8ViAJBICgU8craR')
