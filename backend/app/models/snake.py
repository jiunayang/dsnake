from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, func
from app.core.database import Base


class Snake(Base):
    __tablename__ = "snakes"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, index=True)
    scientific_name = Column(String(200), nullable=True)
    description = Column(Text, nullable=True)
    temperament = Column(String(100), nullable=True)
    treatment = Column(Text, nullable=True)
    is_venomous = Column(Boolean, default=False, index=True)
    image = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
