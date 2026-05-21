import uuid
from datetime import date, datetime

from sqlalchemy import JSON, Boolean, Date, DateTime, Float, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from backend.database import Base


class ClientDB(Base):
    __tablename__ = "clients"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    phone: Mapped[str] = mapped_column(String)
    full_name_cyr: Mapped[str | None] = mapped_column(String, nullable=True)
    full_name_latin: Mapped[str | None] = mapped_column(String, nullable=True)
    date_of_birth: Mapped[date | None] = mapped_column(Date, nullable=True)
    gender: Mapped[str | None] = mapped_column(String, nullable=True)
    citizenship: Mapped[str | None] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)


class ClientPassportDB(Base):
    __tablename__ = "client_passports"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    client_id: Mapped[uuid.UUID]
    series: Mapped[str | None] = mapped_column(String, nullable=True)
    number: Mapped[str | None] = mapped_column(String, nullable=True)
    issued_by: Mapped[str | None] = mapped_column(String, nullable=True)
    issued_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    expiry_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    birth_place: Mapped[str | None] = mapped_column(String, nullable=True)
    mrz_raw: Mapped[str | None] = mapped_column(Text, nullable=True)
    passport_hash: Mapped[str | None] = mapped_column(String, nullable=True)
    is_current: Mapped[bool] = mapped_column(Boolean, default=True)
    ocr_confidence: Mapped[float | None] = mapped_column(Float, nullable=True)
    auto_accepted: Mapped[bool] = mapped_column(Boolean, default=False)
    manual_check: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class IntakeCaseDB(Base):
    __tablename__ = "intake_cases"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    phone: Mapped[str] = mapped_column(String)
    branch: Mapped[str | None] = mapped_column(String, nullable=True)
    resident_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    step: Mapped[str | None] = mapped_column(String, nullable=True)
    status: Mapped[str | None] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)


class IntakeResidentDB(Base):
    __tablename__ = "intake_residents"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    intake_case_id: Mapped[uuid.UUID]
    order_index: Mapped[int] = mapped_column(Integer)
    is_main: Mapped[bool] = mapped_column(Boolean, default=False)
    ocr_data: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    confirmed: Mapped[bool] = mapped_column(Boolean, default=False)
    phone: Mapped[str | None] = mapped_column(String, nullable=True)


class OwnerDB(Base):
    __tablename__ = "owners"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    full_name: Mapped[str] = mapped_column(String)
    phone: Mapped[str] = mapped_column(String)
    payment_day: Mapped[int | None] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class ApartmentDB(Base):
    __tablename__ = "apartments"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    address: Mapped[str] = mapped_column(String)
    rooms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    capacity_residents: Mapped[int | None] = mapped_column(Integer, nullable=True)
    monthly_reg_limit: Mapped[int | None] = mapped_column(Integer, nullable=True)
    current_reg_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    status: Mapped[str | None] = mapped_column(String, nullable=True)
    owner_id: Mapped[uuid.UUID | None] = mapped_column(nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class DealDB(Base):
    __tablename__ = "deals"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    intake_case_id: Mapped[uuid.UUID]
    main_client_id: Mapped[uuid.UUID]
    apartment_id: Mapped[uuid.UUID | None] = mapped_column(nullable=True)
    manager_id: Mapped[str | None] = mapped_column(String, nullable=True)
    branch: Mapped[str | None] = mapped_column(String, nullable=True)
    status: Mapped[str | None] = mapped_column(String, nullable=True)
    date_start: Mapped[date | None] = mapped_column(Date, nullable=True)
    date_end: Mapped[date | None] = mapped_column(Date, nullable=True)
    rent_amount: Mapped[float | None] = mapped_column(Float, nullable=True)
    deposit: Mapped[float | None] = mapped_column(Float, nullable=True)
    commission: Mapped[float | None] = mapped_column(Float, nullable=True)
    registration_fee: Mapped[float | None] = mapped_column(Float, nullable=True)
    contract_url: Mapped[str | None] = mapped_column(String, nullable=True)
    act_url: Mapped[str | None] = mapped_column(String, nullable=True)
    video_url: Mapped[str | None] = mapped_column(String, nullable=True)
    payment_confirmed: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)


class DealResidentDB(Base):
    __tablename__ = "deal_residents"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    deal_id: Mapped[uuid.UUID]
    client_id: Mapped[uuid.UUID]
    is_main: Mapped[bool] = mapped_column(Boolean, default=False)


class OccupancyDB(Base):
    __tablename__ = "occupancies"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    deal_id: Mapped[uuid.UUID]
    client_id: Mapped[uuid.UUID]
    apartment_id: Mapped[uuid.UUID]
    date_start: Mapped[date]
    date_end: Mapped[date]


class RegistrationDB(Base):
    __tablename__ = "registrations"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    deal_id: Mapped[uuid.UUID]
    client_id: Mapped[uuid.UUID]
    apartment_id: Mapped[uuid.UUID]
    date_start: Mapped[date]
    date_end: Mapped[date]
    status: Mapped[str | None] = mapped_column(String, nullable=True)
    mfc_doc_url: Mapped[str | None] = mapped_column(String, nullable=True)


class ClientPaymentDB(Base):
    __tablename__ = "payments_client"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    deal_id: Mapped[uuid.UUID]
    type: Mapped[str] = mapped_column(String)
    amount: Mapped[float] = mapped_column(Float)
    currency: Mapped[str] = mapped_column(String)
    paid_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    confirmed_by: Mapped[str | None] = mapped_column(String, nullable=True)
    payment_method: Mapped[str | None] = mapped_column(String, nullable=True)


class OwnerPaymentDB(Base):
    __tablename__ = "payments_owner"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    owner_id: Mapped[uuid.UUID]
    apartment_id: Mapped[uuid.UUID]
    amount: Mapped[float] = mapped_column(Float)
    currency: Mapped[str] = mapped_column(String)
    planned_date: Mapped[date]
    paid_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    status: Mapped[str | None] = mapped_column(String, nullable=True)


class FileMediaDB(Base):
    __tablename__ = "files_media"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    entity_type: Mapped[str | None] = mapped_column(String, nullable=True)
    entity_id: Mapped[uuid.UUID | None] = mapped_column(nullable=True)
    file_type: Mapped[str | None] = mapped_column(String, nullable=True)
    storage_url: Mapped[str | None] = mapped_column(String, nullable=True)
    metadata_json: Mapped[dict | None] = mapped_column("metadata", JSON, nullable=True)
    uploaded_by: Mapped[str | None] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class AuditLogDB(Base):
    __tablename__ = "audit_logs"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    entity_type: Mapped[str | None] = mapped_column(String, nullable=True)
    entity_id: Mapped[uuid.UUID | None] = mapped_column(nullable=True)
    action: Mapped[str | None] = mapped_column(String, nullable=True)
    actor_id: Mapped[str | None] = mapped_column(String, nullable=True)
    payload: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
