import enum
import uuid
from datetime import datetime

from sqlalchemy import Column, String, Boolean, DateTime, Enum as SAEnum

from api.db.session import Base


class Role(str, enum.Enum):
    PROCUREMENT_OFFICER = "procurement_officer"
    PROCUREMENT_ADMIN = "procurement_admin"
    COMPLIANCE_REVIEWER = "compliance_reviewer"
    DEPARTMENT_ADMIN = "department_admin"
    AUDIT_OFFICER = "audit_officer"
    SENIOR_APPROVING_AUTHORITY = "senior_approving_authority"


def gen_id() -> str:
    return uuid.uuid4().hex


class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=gen_id)
    email = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(SAEnum(Role), nullable=False)
    department = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
