"""Pydantic schemas for request/response validation."""
import datetime as dt
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, EmailStr, Field, field_validator

from app.models import PaymentMethod, TransactionType, UserMode

# Aliases to avoid name collision with Pydantic field names
_date = dt.date
_datetime = dt.datetime


# ---------------------------------------------------------------------------
# Auth
# ---------------------------------------------------------------------------
class RegisterRequest(BaseModel):
    email: EmailStr
    full_name: str
    password: str
    mode: UserMode = UserMode.personal


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: int
    full_name: str
    email: str
    mode: UserMode


class UserResponse(BaseModel):
    id: int
    email: str
    full_name: str
    mode: UserMode
    created_at: _datetime

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# Categories
# ---------------------------------------------------------------------------
class CategoryResponse(BaseModel):
    id: int
    name: str
    slug: str

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# Transactions
# ---------------------------------------------------------------------------
class TransactionCreate(BaseModel):
    amount: Decimal
    type: TransactionType
    description: str
    date: _date = Field(default_factory=dt.date.today)
    category_id: Optional[int] = None
    # UMKM fields
    customer_name: Optional[str] = None
    payment_method: Optional[PaymentMethod] = None

    @field_validator("amount")
    @classmethod
    def amount_positive(cls, v):
        if v <= 0:
            raise ValueError("Nominal harus lebih dari 0")
        return v


class TransactionUpdate(BaseModel):
    amount: Optional[Decimal] = None
    type: Optional[TransactionType] = None
    description: Optional[str] = None
    date: Optional[_date] = None
    category_id: Optional[int] = None
    customer_name: Optional[str] = None
    payment_method: Optional[PaymentMethod] = None


class TransactionResponse(BaseModel):
    id: int
    amount: Decimal
    type: TransactionType
    description: str
    date: _date
    category: Optional[CategoryResponse] = None
    customer_name: Optional[str] = None
    payment_method: Optional[PaymentMethod] = None
    corrected_by_user: bool
    created_at: _datetime

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# Budget
# ---------------------------------------------------------------------------
class BudgetCreate(BaseModel):
    category_id: int
    month: int
    year: int
    limit_amount: Decimal

    @field_validator("month")
    @classmethod
    def valid_month(cls, v):
        if not 1 <= v <= 12:
            raise ValueError("Bulan harus antara 1-12")
        return v

    @field_validator("limit_amount")
    @classmethod
    def limit_positive(cls, v):
        if v <= 0:
            raise ValueError("Anggaran harus lebih dari 0")
        return v


class BudgetResponse(BaseModel):
    id: int
    category: CategoryResponse
    month: int
    year: int
    limit_amount: Decimal
    spent: Decimal = Decimal("0")
    percentage: float = 0.0
    status: str = "aman"  # aman | mendekati | melewati

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# Dashboard / Insights
# ---------------------------------------------------------------------------
class CategoryBreakdown(BaseModel):
    category: str
    slug: str
    total: Decimal
    percentage: float


class MonthSummary(BaseModel):
    month: int
    year: int
    total_income: Decimal
    total_expense: Decimal
    balance: Decimal
    breakdown: list[CategoryBreakdown]
    insights: list[str]


class TrendPoint(BaseModel):  # noqa: F811
    month: int
    year: int
    label: str
    total_income: Decimal
    total_expense: Decimal


# ---------------------------------------------------------------------------
# Category Correction
# ---------------------------------------------------------------------------
class CategoryCorrectionCreate(BaseModel):
    transaction_id: int
    corrected_category_id: int
