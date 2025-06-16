from fastapi import APIRouter, Depends, Request
from app.core.auth import get_current_user
from app.core.limiter import limiter

router = APIRouter()

@router.get("/public")
@limiter.limit("10/minute")
def public_route(request: Request):
    return {"message": "Public route with IP-based rate limit"}

@router.get("/protected")
@limiter.limit("5/minute")
def protected_route(request: Request, user=Depends(get_current_user)):
    return {"message": f"Welcome {user}"} 