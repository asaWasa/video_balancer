from ..database import get_db
from ..r_cache import get_redis_client
from ..schemas import BalancerRequest, BalancerResponse
from src.app.balancer import video_balancer

from fastapi import APIRouter, Depends, Query
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

import logging

logger = logging.getLogger(__name__)

router = APIRouter(tags=["balancer"])


@router.get("/", response_class=RedirectResponse)
async def balance_video_request(
    video: str = Query(..., description="Video URL to balance"),
    db: AsyncSession = Depends(get_db),
    redis_cache=Depends(get_redis_client),
):
    """
    Main balancer endpoint

    Example:
        GET /?video=http://s1.origin-cluster/video/1488/xcg2djHckad.m3u8
    """

    redirect_url, target = await video_balancer.balance_request(video, db, redis_cache)

    return RedirectResponse(
        url=redirect_url,
        status_code=301,
        headers={"X-Target": target, "X-Original-URL": video},
    )


@router.post("/balance", response_model=BalancerResponse)
async def balance_video_request_json(
    request: BalancerRequest, db: AsyncSession = Depends(get_db)
):
    redirect_url, target = await video_balancer.balance_request(request.video, db)
    return BalancerResponse(redirect_url=redirect_url, target=target)


@router.get("/stats")
async def get_balancer_stats():
    """
    Get current balancer statistics
    """
    stats = {
        "request_counter": video_balancer.request_counter,
        "balancer_status": "active",
    }
    return stats


@router.post("/reset")
async def reset_balancer_counter():
    """
    Reset balancer request counter
    """
    video_balancer.reset_counter()
    return {"message": "Balancer counter reset successfully"}
