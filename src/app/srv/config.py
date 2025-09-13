import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from ..database import get_db
from ..crud import balancer_config_crud
from ..schemas import (
    BalancerConfigCreate,
    BalancerConfigUpdate,
    BalancerConfigResponse,
    DelMessageResponse,
)

logger = logging.getLogger(__name__)

# todo на сервисные ручки обычно накидывается авторизация

router = APIRouter(prefix="/srv/config", tags=["config"])


@router.get("/", response_model=BalancerConfigResponse)
async def get_active_config(db: AsyncSession = Depends(get_db)):
    """Get the currently active balancer configuration"""
    logger.debug("Retrieving active balancer configuration")
    config = await balancer_config_crud.get_active_config(db)
    if not config:
        logger.warning("No active configuration found")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active configuration found",
        )
    logger.debug(
        f"Active configuration retrieved: ID={config.id}, CDN={config.cdn_host}"
    )
    return config


@router.get("/all", response_model=List[BalancerConfigResponse])
async def get_all_configs(db: AsyncSession = Depends(get_db)):
    """Get all balancer configurations"""
    logger.debug("Retrieving all balancer configurations")
    configs = await balancer_config_crud.get_all_configs(db)
    logger.debug(f"Retrieved {len(configs)} configurations")
    return configs


@router.get("/{config_id}", response_model=BalancerConfigResponse)
async def get_config_by_id(config_id: int, db: AsyncSession = Depends(get_db)):
    """Get configuration by ID"""
    if config := await balancer_config_crud.get_config_by_id(db, config_id):
        return config
    raise HTTPException(status_code=404, detail="Configuration not found")


@router.post("/", response_model=BalancerConfigResponse)
async def create_config(
    config: BalancerConfigCreate, db: AsyncSession = Depends(get_db)
):
    """Create new config."""
    logger.debug(
        f"Creating new balancer configuration: CDN={config.cdn_host}, ratio={config.cdn_ratio}:{config.origin_ratio}"
    )

    if config.cdn_ratio + config.origin_ratio != 10:
        logger.error(
            f"Invalid ratio configuration: {config.cdn_ratio} + {config.origin_ratio} != 10"
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="CDN ratio + Origin ratio must equal 10",
        )

    new_config = await balancer_config_crud.create_config(db, config)
    logger.debug(f"New configuration created with ID: {new_config.id}")
    return new_config


@router.put("/{config_id}", response_model=BalancerConfigResponse)
async def update_config(
    config_id: int, config: BalancerConfigUpdate, db: AsyncSession = Depends(get_db)
):
    """Update balancer config"""
    if config.cdn_ratio is not None and config.origin_ratio is not None:
        if config.cdn_ratio + config.origin_ratio != 10:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="CDN ratio + Origin ratio must equal 10",
            )

    updated_config = await balancer_config_crud.update_config(db, config_id, config)
    if not updated_config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Configuration not found"
        )
    return updated_config


@router.delete("/{config_id}", response_model=DelMessageResponse)
async def delete_config(config_id: int, db: AsyncSession = Depends(get_db)):
    """Delete balancer config"""
    success = await balancer_config_crud.delete_config(db, config_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Configuration not found"
        )
    return {"message": "Configuration deleted successfully"}


@router.post("/{config_id}/activate", response_model=BalancerConfigResponse)
async def activate_config(config_id: int, db: AsyncSession = Depends(get_db)):
    """Activate config"""
    config = await balancer_config_crud.activate_config(db, config_id)
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Configuration not found"
        )
    return config
