from slowapi import Limiter
from slowapi.util import get_remote_address
from app.core.auth import get_api_key

limiter = Limiter(key_func=get_remote_address) 