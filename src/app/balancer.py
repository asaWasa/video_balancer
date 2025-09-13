from config import CDN_HOST, DEFAULT_CDN_RATIO, DEFAULT_ORIGIN_RATIO
from src.app.crud import balancer_config_crud
from src.app.schemas import BalancerConfigUpdate

from sqlalchemy.ext.asyncio import AsyncSession

from typing import Tuple
from urllib.parse import urlparse
import logging
import re
import json


logger = logging.getLogger(__name__)


class VideoBalancer:
    """Video request balancer that routes requests to CDN or origin servers"""

    def __init__(self):
        self.request_counter = 0

    def _parse_video_url(self, video_url: str) -> Tuple[str, str, str]:
        """
        Parse video URL to extract server, path and filename
        Expected format: http://s1.origin-cluster/video/1488/xcg2djHckad.m3u8

        Returns:
            Tuple of (server, path, filename)
        """

        try:
            parsed = urlparse(video_url)
            hostname = parsed.hostname

            if not hostname:
                raise ValueError("Invalid hostname in URL")

            server_match = re.match(r"^([a-zA-Z0-9]+)\.", hostname)
            if not server_match:
                raise ValueError(f"Invalid server format in hostname: {hostname}")

            server = server_match.group(1)
            path = parsed.path

            if not path or not path.startswith("/"):
                raise ValueError("Invalid path format")

            if not re.match(r"^/video/\d+/[a-zA-Z0-9_-]", path):
                raise ValueError("Path does not match expected video format")

            return server, path, hostname

        except Exception as e:
            raise ValueError(f"Invalid video URL format: {video_url}. Error: {str(e)}")

    def _generate_cdn_url(self, server: str, path: str, cdn_host: str) -> str:
        """
        Generate CDN URL from server and path
        Format: http://{cdn_host}/{server}{path}
        """
        return f"http://{cdn_host}/{server}{path}"

    def _should_use_origin(self, cdn_ratio: int, origin_ratio: int) -> bool:
        """
        Determine if request should go to origin based on ratios
        Uses simple round-robin approach for better distribution
        """
        total_ratio = cdn_ratio + origin_ratio
        self.request_counter += 1

        return (self.request_counter % total_ratio) < origin_ratio

    async def balance_request(
        self,
        video_url: str,
        db: AsyncSession,
        redis_cache,
    ) -> Tuple[str, str]:
        """
        Balance video request between CDN and origin

        Args:
            video_url: Original video URL
            db: Database session
            redis_cache: Cache

        Returns:
            Tuple of (redirect_url, target_type)
        """
        server, path, _ = self._parse_video_url(video_url)

        try:

            config = await self._get_conf(db, redis_cache)

            if config:
                cdn_host = config.cdn_host
                cdn_ratio = config.cdn_ratio
                origin_ratio = config.origin_ratio
            else:
                cdn_host = CDN_HOST
                cdn_ratio = DEFAULT_CDN_RATIO
                origin_ratio = DEFAULT_ORIGIN_RATIO

            if self._should_use_origin(cdn_ratio, origin_ratio):
                return video_url, "origin"
            else:
                cdn_url = self._generate_cdn_url(server, path, cdn_host)
                return cdn_url, "cdn"

        except Exception as e:
            logger.warning(
                f"⚠️  Warning: Using fallback to origin due to configuration error: {e}"
            )
            return video_url, "origin"

    async def _get_conf(self, db, cache):
        try:
            if cached_config := await cache.get("balancer_config"):
                cached = json.loads(cached_config)
                logger.info("Cached ok %s", cached)
                return BalancerConfigUpdate(**cached)
        except Exception as e:
            logger.warning("Redis cache warning %s", e)

        if config := await balancer_config_crud.get_active_config(db):
            try:
                config_dict = {
                    "cdn_host": config.cdn_host,
                    "cdn_ratio": config.cdn_ratio,
                    "origin_ratio": config.origin_ratio,
                    "is_active": config.is_active,
                }
                await cache.setex("balancer_config", 300, json.dumps(config_dict))
            except Exception as e:
                logger.warning(f"Failed to set Redis cache: {e}")
            return config

        return BalancerConfigUpdate(
            cdn_host=CDN_HOST,
            cdn_ratio=DEFAULT_CDN_RATIO,
            origin_ratio=DEFAULT_ORIGIN_RATIO,
            is_active=True,
        )

    def reset_counter(self):
        """Reset request counter (useful for testing)"""
        self.request_counter = 0


video_balancer = VideoBalancer()
