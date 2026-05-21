"""initial schema

Revision ID: 001_initial_schema
Revises:
Create Date: 2026-05-21
"""

from alembic import op
import sqlalchemy as sa


revision = "001_initial_schema"
down_revision = None
branch_labels = None
depends_on = None


def _uuid_col(name: str, nullable: bool = False):
    return sa.Column(name, sa.UUID(), nullable=nullable)


def upgrade() -> None:
    op.create_table(
        "clients",
        _uuid_col("id"),
        sa.Column("phone", sa.String(), nullable=False),
        sa.Column("full_name_cyr", sa.String(), nullable=True),
        sa.Column("full_name_latin", sa.String(), nullable=True),
        sa.Column("date_of_birth", sa.Date(), nullable=True),
        sa.Column("gender", sa.String(), nullable=True),
        sa.Column("citizenship", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "client_passports",
        _uuid_col("id"), _uuid_col("client_id"), sa.Column("series", sa.String(), nullable=True),
        sa.Column("number", sa.String(), nullable=True), sa.Column("issued_by", sa.String(), nullable=True),
        sa.Column("issued_date", sa.Date(), nullable=True), sa.Column("expiry_date", sa.Date(), nullable=True),
        sa.Column("birth_place", sa.String(), nullable=True), sa.Column("mrz_raw", sa.Text(), nullable=True),
        sa.Column("passport_hash", sa.String(), nullable=True), sa.Column("is_current", sa.Boolean(), nullable=False),
        sa.Column("ocr_confidence", sa.Float(), nullable=True), sa.Column("auto_accepted", sa.Boolean(), nullable=False),
        sa.Column("manual_check", sa.Boolean(), nullable=False), sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table("intake_cases", _uuid_col("id"), sa.Column("phone", sa.String(), nullable=False), sa.Column("branch", sa.String(), nullable=True), sa.Column("resident_count", sa.Integer(), nullable=True), sa.Column("step", sa.String(), nullable=True), sa.Column("status", sa.String(), nullable=True), sa.Column("created_at", sa.DateTime(), nullable=False), sa.Column("updated_at", sa.DateTime(), nullable=True), sa.PrimaryKeyConstraint("id"))
    op.create_table("intake_residents", _uuid_col("id"), _uuid_col("intake_case_id"), sa.Column("order_index", sa.Integer(), nullable=False), sa.Column("is_main", sa.Boolean(), nullable=False), sa.Column("ocr_data", sa.JSON(), nullable=True), sa.Column("confirmed", sa.Boolean(), nullable=False), sa.Column("phone", sa.String(), nullable=True), sa.PrimaryKeyConstraint("id"))
    op.create_table("owners", _uuid_col("id"), sa.Column("full_name", sa.String(), nullable=False), sa.Column("phone", sa.String(), nullable=False), sa.Column("payment_day", sa.Integer(), nullable=True), sa.Column("created_at", sa.DateTime(), nullable=False), sa.PrimaryKeyConstraint("id"))
    op.create_table("apartments", _uuid_col("id"), sa.Column("address", sa.String(), nullable=False), sa.Column("rooms", sa.Integer(), nullable=True), sa.Column("capacity_residents", sa.Integer(), nullable=True), sa.Column("monthly_reg_limit", sa.Integer(), nullable=True), sa.Column("current_reg_count", sa.Integer(), nullable=True), sa.Column("status", sa.String(), nullable=True), _uuid_col("owner_id", nullable=True), sa.Column("created_at", sa.DateTime(), nullable=False), sa.PrimaryKeyConstraint("id"))
    op.create_table("deals", _uuid_col("id"), _uuid_col("intake_case_id"), _uuid_col("main_client_id"), _uuid_col("apartment_id", nullable=True), sa.Column("manager_id", sa.String(), nullable=True), sa.Column("branch", sa.String(), nullable=True), sa.Column("status", sa.String(), nullable=True), sa.Column("date_start", sa.Date(), nullable=True), sa.Column("date_end", sa.Date(), nullable=True), sa.Column("rent_amount", sa.Float(), nullable=True), sa.Column("deposit", sa.Float(), nullable=True), sa.Column("commission", sa.Float(), nullable=True), sa.Column("registration_fee", sa.Float(), nullable=True), sa.Column("contract_url", sa.String(), nullable=True), sa.Column("act_url", sa.String(), nullable=True), sa.Column("video_url", sa.String(), nullable=True), sa.Column("payment_confirmed", sa.Boolean(), nullable=False), sa.Column("created_at", sa.DateTime(), nullable=False), sa.Column("updated_at", sa.DateTime(), nullable=True), sa.PrimaryKeyConstraint("id"))
    op.create_table("deal_residents", _uuid_col("id"), _uuid_col("deal_id"), _uuid_col("client_id"), sa.Column("is_main", sa.Boolean(), nullable=False), sa.PrimaryKeyConstraint("id"))
    op.create_table("occupancies", _uuid_col("id"), _uuid_col("deal_id"), _uuid_col("client_id"), _uuid_col("apartment_id"), sa.Column("date_start", sa.Date(), nullable=False), sa.Column("date_end", sa.Date(), nullable=False), sa.PrimaryKeyConstraint("id"))
    op.create_table("registrations", _uuid_col("id"), _uuid_col("deal_id"), _uuid_col("client_id"), _uuid_col("apartment_id"), sa.Column("date_start", sa.Date(), nullable=False), sa.Column("date_end", sa.Date(), nullable=False), sa.Column("status", sa.String(), nullable=True), sa.Column("mfc_doc_url", sa.String(), nullable=True), sa.PrimaryKeyConstraint("id"))
    op.create_table("payments_client", _uuid_col("id"), _uuid_col("deal_id"), sa.Column("type", sa.String(), nullable=False), sa.Column("amount", sa.Float(), nullable=False), sa.Column("currency", sa.String(), nullable=False), sa.Column("paid_at", sa.DateTime(), nullable=True), sa.Column("confirmed_by", sa.String(), nullable=True), sa.Column("payment_method", sa.String(), nullable=True), sa.PrimaryKeyConstraint("id"))
    op.create_table("payments_owner", _uuid_col("id"), _uuid_col("owner_id"), _uuid_col("apartment_id"), sa.Column("amount", sa.Float(), nullable=False), sa.Column("currency", sa.String(), nullable=False), sa.Column("planned_date", sa.Date(), nullable=False), sa.Column("paid_at", sa.DateTime(), nullable=True), sa.Column("status", sa.String(), nullable=True), sa.PrimaryKeyConstraint("id"))
    op.create_table("files_media", _uuid_col("id"), sa.Column("entity_type", sa.String(), nullable=True), _uuid_col("entity_id", nullable=True), sa.Column("file_type", sa.String(), nullable=True), sa.Column("storage_url", sa.String(), nullable=True), sa.Column("metadata", sa.JSON(), nullable=True), sa.Column("uploaded_by", sa.String(), nullable=True), sa.Column("created_at", sa.DateTime(), nullable=False), sa.PrimaryKeyConstraint("id"))
    op.create_table("audit_logs", _uuid_col("id"), sa.Column("entity_type", sa.String(), nullable=True), _uuid_col("entity_id", nullable=True), sa.Column("action", sa.String(), nullable=True), sa.Column("actor_id", sa.String(), nullable=True), sa.Column("payload", sa.JSON(), nullable=True), sa.Column("created_at", sa.DateTime(), nullable=False), sa.PrimaryKeyConstraint("id"))


def downgrade() -> None:
    for table in [
        "audit_logs", "files_media", "payments_owner", "payments_client", "registrations", "occupancies",
        "deal_residents", "deals", "apartments", "owners", "intake_residents", "intake_cases", "client_passports", "clients",
    ]:
        op.drop_table(table)
