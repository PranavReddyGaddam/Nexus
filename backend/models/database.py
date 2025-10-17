from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean
from sqlalchemy.sql import func
from config.database import Base

class Session(Base):
    __tablename__ = "sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    product_idea = Column(Text, nullable=False)
    status = Column(String(20), default="processing")  # processing, completed, failed
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

class AnalysisResult(Base):
    __tablename__ = "analysis_results"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, nullable=False)
    personas = Column(Text)  # JSON string
    opinions = Column(Text)  # JSON string
    summary = Column(Text)
    sentiment_breakdown = Column(Text)  # JSON string
    market_potential = Column(String(20))  # high, medium, low
    confidence_score = Column(Integer)  # 0-100
    created_at = Column(DateTime, default=func.now())
