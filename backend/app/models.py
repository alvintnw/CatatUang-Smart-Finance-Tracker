import enum
from datetime import date, datetime

from sqlalchemy import (
    BigInteger,
    Boolean,
    Column,
    Date,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import relationship

from app.database import Base


class UserMode(str, enum.Enum):
    personal = "personal"
    umkm = "umkm"


class TransactionType(str, enum.Enum):
    income = "income"
    expense = "expense"


class PaymentMethod(str, enum.Enum):
    tunai = "tunai"
    qris = "qris"
    transfer = "transfer"


# ---------------------------------------------------------------------------
# Category (seeded at startup)
# ---------------------------------------------------------------------------
class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)   # display name, e.g. "Makanan"
    slug = Column(String(50), unique=True, nullable=False)  # e.g. "makanan"

    transactions = relationship("Transaction", back_populates="category")
    budgets = relationship("Budget", back_populates="category")
    corrections_predicted = relationship(
        "CategoryCorrection",
        foreign_keys="CategoryCorrection.predicted_category_id",
        back_populates="predicted_category",
    )
    corrections_corrected = relationship(
        "CategoryCorrection",
        foreign_keys="CategoryCorrection.corrected_category_id",
        back_populates="corrected_category",
    )


# ---------------------------------------------------------------------------
# User
# ---------------------------------------------------------------------------
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    full_name = Column(String(255), nullable=False)
    password_hash = Column(String(255), nullable=False)
    mode = Column(Enum(UserMode), default=UserMode.personal, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    transactions = relationship("Transaction", back_populates="user", cascade="all, delete")
    budgets = relationship("Budget", back_populates="user", cascade="all, delete")
    corrections = relationship("CategoryCorrection", back_populates="user", cascade="all, delete")


# ---------------------------------------------------------------------------
# Transaction
# ---------------------------------------------------------------------------
class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    amount = Column(Numeric(15, 2), nullable=False)
    type = Column(Enum(TransactionType), nullable=False)
    description = Column(Text, nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    date = Column(Date, nullable=False, default=date.today)

    # UMKM-specific optional fields
    customer_name = Column(String(255), nullable=True)
    payment_method = Column(Enum(PaymentMethod), nullable=True)

    # Whether the user has manually corrected the auto-category
    corrected_by_user = Column(Boolean, default=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    user = relationship("User", back_populates="transactions")
    category = relationship("Category", back_populates="transactions")


# ---------------------------------------------------------------------------
# Budget
# ---------------------------------------------------------------------------
class Budget(Base):
    __tablename__ = "budgets"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)
    month = Column(Integer, nullable=False)   # 1-12
    year = Column(Integer, nullable=False)
    limit_amount = Column(Numeric(15, 2), nullable=False)

    __table_args__ = (
        UniqueConstraint("user_id", "category_id", "month", "year", name="uq_budget_user_cat_month"),
    )

    user = relationship("User", back_populates="budgets")
    category = relationship("Category", back_populates="budgets")


# ---------------------------------------------------------------------------
# Category Correction  (training data for future ML)
# ---------------------------------------------------------------------------
class CategoryCorrection(Base):
    __tablename__ = "category_corrections"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    description = Column(Text, nullable=False)
    predicted_category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    corrected_category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="corrections")
    predicted_category = relationship(
        "Category",
        foreign_keys=[predicted_category_id],
        back_populates="corrections_predicted",
    )
    corrected_category = relationship(
        "Category",
        foreign_keys=[corrected_category_id],
        back_populates="corrections_corrected",
    )
