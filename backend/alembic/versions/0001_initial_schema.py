"""initial schema

Revision ID: 0001
Revises: 
Create Date: 2024-01-01 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # categories
    op.create_table(
        "categories",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("slug", sa.String(50), unique=True, nullable=False),
    )

    # Seed default categories
    op.bulk_insert(
        sa.table(
            "categories",
            sa.column("id", sa.Integer),
            sa.column("name", sa.String),
            sa.column("slug", sa.String),
        ),
        [
            {"id": 1,  "name": "Makanan & Minuman", "slug": "makanan"},
            {"id": 2,  "name": "Transportasi",      "slug": "transportasi"},
            {"id": 3,  "name": "Tagihan & Utilitas","slug": "tagihan"},
            {"id": 4,  "name": "Belanja",            "slug": "belanja"},
            {"id": 5,  "name": "Hiburan",            "slug": "hiburan"},
            {"id": 6,  "name": "Pendidikan",         "slug": "pendidikan"},
            {"id": 7,  "name": "Kesehatan",          "slug": "kesehatan"},
            {"id": 8,  "name": "Gaji & Pendapatan",  "slug": "gaji"},
            {"id": 9,  "name": "Lain-lain",          "slug": "lain-lain"},
        ],
    )

    # users
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("email", sa.String(255), unique=True, nullable=False),
        sa.Column("full_name", sa.String(255), nullable=False),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("mode", sa.Enum("personal", "umkm", name="usermode"), default="personal", nullable=False),
        sa.Column("is_active", sa.Boolean(), default=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_users_email", "users", ["email"])

    # transactions
    op.create_table(
        "transactions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("amount", sa.Numeric(15, 2), nullable=False),
        sa.Column("type", sa.Enum("income", "expense", name="transactiontype"), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("category_id", sa.Integer(), sa.ForeignKey("categories.id"), nullable=True),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("customer_name", sa.String(255), nullable=True),
        sa.Column("payment_method", sa.Enum("tunai", "qris", "transfer", name="paymentmethod"), nullable=True),
        sa.Column("corrected_by_user", sa.Boolean(), default=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), onupdate=sa.func.now()),
    )
    op.create_index("ix_transactions_user_id", "transactions", ["user_id"])
    op.create_index("ix_transactions_date", "transactions", ["date"])

    # budgets
    op.create_table(
        "budgets",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("category_id", sa.Integer(), sa.ForeignKey("categories.id"), nullable=False),
        sa.Column("month", sa.Integer(), nullable=False),
        sa.Column("year", sa.Integer(), nullable=False),
        sa.Column("limit_amount", sa.Numeric(15, 2), nullable=False),
        sa.UniqueConstraint("user_id", "category_id", "month", "year", name="uq_budget_user_cat_month"),
    )

    # category_corrections
    op.create_table(
        "category_corrections",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("predicted_category_id", sa.Integer(), sa.ForeignKey("categories.id"), nullable=True),
        sa.Column("corrected_category_id", sa.Integer(), sa.ForeignKey("categories.id"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table("category_corrections")
    op.drop_table("budgets")
    op.drop_table("transactions")
    op.drop_table("users")
    op.drop_table("categories")
    op.execute("DROP TYPE IF EXISTS usermode")
    op.execute("DROP TYPE IF EXISTS transactiontype")
    op.execute("DROP TYPE IF EXISTS paymentmethod")
