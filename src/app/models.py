from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.sql import func
from .database import Base


class BalancerConfig(Base):
    __tablename__ = "balancer_configs"
    
    id = Column(Integer, primary_key=True, index=True)
    cdn_host = Column(String(255), nullable=False, default="cdn.example.com")
    cdn_ratio = Column(Integer, nullable=False, default=9)
    origin_ratio = Column(Integer, nullable=False, default=1)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<BalancerConfig(id={self.id}, cdn_host='{self.cdn_host}', cdn_ratio={self.cdn_ratio}, origin_ratio={self.origin_ratio})>"



