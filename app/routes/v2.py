from fastapi import APIRouter, Depends, Request
from app.core.auth import get_api_key

router = APIRouter()

@router.get("/data")
def data_route(request: Request, api_key=Depends(get_api_key)):
    return {"data": "This is v2 route with API Key validation"} 