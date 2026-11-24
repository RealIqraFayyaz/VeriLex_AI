from datetime import datetime, timezone
from sqlalchemy import String, DateTime, ForeignKey, Integer, Text, JSON, Enum, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base
import enum
def utcnow(): return datetime.now(timezone.utc)
class Role(str, enum.Enum):
    SUPER_ADMIN="SUPER_ADMIN"; ADMIN="ADMIN"; INSTRUCTOR="INSTRUCTOR"; STUDENT="STUDENT"; RESEARCHER="RESEARCHER"
class User(Base):
    __tablename__="users"
    id: Mapped[int]=mapped_column(primary_key=True)
    full_name: Mapped[str]=mapped_column(String(160))
    email: Mapped[str]=mapped_column(String(255),unique=True,index=True)
    password_hash: Mapped[str]=mapped_column(String(255))
    role: Mapped[Role]=mapped_column(Enum(Role),default=Role.STUDENT)
    is_active: Mapped[bool]=mapped_column(Boolean,default=True)
    created_at: Mapped[datetime]=mapped_column(DateTime(timezone=True),default=utcnow)
class Document(Base):
    __tablename__="documents"
    id: Mapped[int]=mapped_column(primary_key=True)
    owner_id: Mapped[int]=mapped_column(ForeignKey("users.id",ondelete="CASCADE"),index=True)
    filename: Mapped[str]=mapped_column(String(255))
    file_type: Mapped[str]=mapped_column(String(20))
    file_size: Mapped[int]=mapped_column(Integer)
    storage_path: Mapped[str]=mapped_column(String(700))
    extracted_text: Mapped[str]=mapped_column(Text,default="")
    detected_language: Mapped[str]=mapped_column(String(30),default="unknown")
    created_at: Mapped[datetime]=mapped_column(DateTime(timezone=True),default=utcnow)
class AnalysisJob(Base):
    __tablename__="analysis_jobs"
    id: Mapped[int]=mapped_column(primary_key=True)
    user_id: Mapped[int]=mapped_column(ForeignKey("users.id",ondelete="CASCADE"),index=True)
    document_id: Mapped[int]=mapped_column(ForeignKey("documents.id",ondelete="CASCADE"),index=True)
    analysis_type: Mapped[str]=mapped_column(String(40),default="complete")
    status: Mapped[str]=mapped_column(String(30),default="QUEUED")
    progress: Mapped[int]=mapped_column(Integer,default=0)
    error_message: Mapped[str|None]=mapped_column(Text,nullable=True)
    result_json: Mapped[dict|None]=mapped_column(JSON,nullable=True)
    created_at: Mapped[datetime]=mapped_column(DateTime(timezone=True),default=utcnow)
    completed_at: Mapped[datetime|None]=mapped_column(DateTime(timezone=True),nullable=True)
