from fastapi import HTTPException, Request, Security
from fastapi.security import APIKeyHeader
from jose import JWTError, jwt
from app.core.config import settings

api_key_header = APIKeyHeader(name="X-API-Key")

def verify_jwt_token(token: str):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload.get("sub")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

def get_current_user(request: Request):
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    return verify_jwt_token(token)

def get_api_key(api_key: str = Security(api_key_header)):
    if api_key != settings.API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API key")
    return api_key 