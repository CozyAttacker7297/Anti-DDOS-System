from fastapi import APIRouter
from ..utils import get_stats, get_uptime

router = APIRouter()

@router.get("/dashboard/stats")
def dashboard_stats():
    return get_stats()

@router.get("/dashboard/uptime")
def dashboard_uptime():
    return get_uptime() 