from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from .models import BalancerConfig
from .schemas import BalancerConfigCreate, BalancerConfigUpdate
from typing import List


class BalancerConfigCRUD:
    @staticmethod
    async def get_active_config(db: AsyncSession) -> BalancerConfig | None:
        """Get the active balancer configuration"""
        result = await db.execute(
            select(BalancerConfig).where(BalancerConfig.is_active == True)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_config_by_id(
        db: AsyncSession, config_id: int
    ) -> BalancerConfig | None:
        """Get configuration by ID"""
        result = await db.execute(
            select(BalancerConfig).where(BalancerConfig.id == config_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_all_configs(db: AsyncSession) -> List[BalancerConfig]:
        """Get all configurations"""
        result = await db.execute(select(BalancerConfig))
        return result.scalars().all()

    @staticmethod
    async def create_config(
        db: AsyncSession, config: BalancerConfigCreate
    ) -> BalancerConfig:
        """Create new configuration"""
        async with db.begin():
            await db.execute(
                update(BalancerConfig)
                .where(BalancerConfig.is_active == True)
                .values(is_active=False)
            )
            db_config = BalancerConfig(**config.model_dump())
            db.add(db_config)
        await db.commit()
        await db.refresh(db_config)
        return db_config

    @staticmethod
    async def update_config(
        db: AsyncSession, config_id: int, config: BalancerConfigUpdate
    ) -> BalancerConfig | None:
        """Update configuration"""
        update_data = config.model_dump(exclude_unset=True)
        if not update_data:
            return await BalancerConfigCRUD.get_config_by_id(db, config_id)

        await db.execute(
            update(BalancerConfig)
            .where(BalancerConfig.id == config_id)
            .values(**update_data)
        )
        await db.commit()
        return await BalancerConfigCRUD.get_config_by_id(db, config_id)

    @staticmethod
    async def delete_config(db: AsyncSession, config_id: int) -> bool:
        """Delete configuration"""
        result = await db.execute(
            delete(BalancerConfig).where(BalancerConfig.id == config_id)
        )
        await db.commit()
        return result.rowcount > 0

    @staticmethod
    async def activate_config(
        db: AsyncSession, config_id: int
    ) -> BalancerConfig | None:
        """Activate specific configuration"""
        await db.execute(update(BalancerConfig).values(is_active=False))

        await db.execute(
            update(BalancerConfig)
            .where(BalancerConfig.id == config_id)
            .values(is_active=True)
        )
        await db.commit()
        return await BalancerConfigCRUD.get_config_by_id(db, config_id)


balancer_config_crud = BalancerConfigCRUD()
