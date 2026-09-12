"""
Dashboard & insight engine.

Insight generation is intentionally simple text logic here.
It can be enhanced or replaced with an LLM call without changing the router
contract — just edit the _generate_insights() function.
"""
from collections import defaultdict
from datetime import date
from decimal import Decimal
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from app import models, schemas
from app.auth import get_current_user
from app.database import get_db

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])

IDR_FMT = lambda v: f"Rp {int(v):,}".replace(",", ".")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _sum_by_type(db: Session, user_id: int, month: int, year: int, tx_type: models.TransactionType) -> Decimal:
    result = (
        db.query(func.coalesce(func.sum(models.Transaction.amount), 0))
        .filter(
            models.Transaction.user_id == user_id,
            models.Transaction.type == tx_type,
            func.extract("month", models.Transaction.date) == month,
            func.extract("year", models.Transaction.date) == year,
        )
        .scalar()
    )
    return Decimal(str(result))


def _expense_by_category(db: Session, user_id: int, month: int, year: int) -> dict:
    rows = (
        db.query(models.Category.name, models.Category.slug, func.sum(models.Transaction.amount).label("total"))
        .join(models.Transaction, models.Transaction.category_id == models.Category.id)
        .filter(
            models.Transaction.user_id == user_id,
            models.Transaction.type == models.TransactionType.expense,
            func.extract("month", models.Transaction.date) == month,
            func.extract("year", models.Transaction.date) == year,
        )
        .group_by(models.Category.name, models.Category.slug)
        .order_by(func.sum(models.Transaction.amount).desc())
        .all()
    )
    return rows


def _generate_insights(
    breakdown: list[schemas.CategoryBreakdown],
    prev_breakdown: list[schemas.CategoryBreakdown],
    total_expense: Decimal,
    prev_total_expense: Decimal,
    month_label: str,
) -> list[str]:
    insights = []

    if not breakdown:
        insights.append("Belum ada transaksi pengeluaran bulan ini.")
        return insights

    # Biggest expense category
    top = breakdown[0]
    insights.append(
        f"Pengeluaran terbesar bulan ini adalah kategori \"{top.category}\" "
        f"sebesar {IDR_FMT(top.total)} ({top.percentage:.0f}% dari total)."
    )

    # Month-over-month total change
    if prev_total_expense > 0:
        change_pct = float((total_expense - prev_total_expense) / prev_total_expense * 100)
        direction = "naik" if change_pct > 0 else "turun"
        insights.append(
            f"Total pengeluaran {direction} {abs(change_pct):.0f}% dibanding bulan sebelumnya."
        )

    # Per-category month-over-month change
    prev_map = {row.slug: row.total for row in prev_breakdown}
    for row in breakdown:
        prev_total = prev_map.get(row.slug, Decimal("0"))
        if prev_total > 0:
            change_pct = float((row.total - prev_total) / prev_total * 100)
            if abs(change_pct) >= 20:
                direction = "naik" if change_pct > 0 else "turun"
                insights.append(
                    f"Pengeluaran kategori \"{row.category}\" {direction} "
                    f"{abs(change_pct):.0f}% dibanding bulan lalu."
                )

    return insights


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------
@router.get("/summary", response_model=schemas.MonthSummary)
def summary(
    month: Optional[int] = Query(None, ge=1, le=12),
    year: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    today = date.today()
    month = month or today.month
    year = year or today.year

    total_income = _sum_by_type(db, current_user.id, month, year, models.TransactionType.income)
    total_expense = _sum_by_type(db, current_user.id, month, year, models.TransactionType.expense)
    balance = total_income - total_expense

    # Breakdown
    rows = _expense_by_category(db, current_user.id, month, year)
    breakdown = [
        schemas.CategoryBreakdown(
            category=r.name,
            slug=r.slug,
            total=Decimal(str(r.total)),
            percentage=round(float(r.total / total_expense * 100), 1) if total_expense > 0 else 0.0,
        )
        for r in rows
    ]

    # Previous month for insight comparison
    prev_month = month - 1 if month > 1 else 12
    prev_year = year if month > 1 else year - 1
    prev_total_expense = _sum_by_type(db, current_user.id, prev_month, prev_year, models.TransactionType.expense)
    prev_rows = _expense_by_category(db, current_user.id, prev_month, prev_year)
    prev_breakdown = [
        schemas.CategoryBreakdown(
            category=r.name,
            slug=r.slug,
            total=Decimal(str(r.total)),
            percentage=0.0,
        )
        for r in prev_rows
    ]

    MONTHS_ID = ["", "Jan", "Feb", "Mar", "Apr", "Mei", "Jun", "Jul", "Ags", "Sep", "Okt", "Nov", "Des"]
    insights = _generate_insights(
        breakdown, prev_breakdown, total_expense, prev_total_expense, MONTHS_ID[month]
    )

    return schemas.MonthSummary(
        month=month,
        year=year,
        total_income=total_income,
        total_expense=total_expense,
        balance=balance,
        breakdown=breakdown,
        insights=insights,
    )


@router.get("/trend", response_model=list[schemas.TrendPoint])
def trend(
    months: int = Query(6, ge=2, le=12),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """Returns income/expense totals for the last N months."""
    MONTHS_ID = ["", "Jan", "Feb", "Mar", "Apr", "Mei", "Jun", "Jul", "Ags", "Sep", "Okt", "Nov", "Des"]
    today = date.today()
    points = []

    for i in range(months - 1, -1, -1):
        m = today.month - i
        y = today.year
        while m <= 0:
            m += 12
            y -= 1

        income = _sum_by_type(db, current_user.id, m, y, models.TransactionType.income)
        expense = _sum_by_type(db, current_user.id, m, y, models.TransactionType.expense)
        points.append(
            schemas.TrendPoint(
                month=m,
                year=y,
                label=f"{MONTHS_ID[m]} {y}",
                total_income=income,
                total_expense=expense,
            )
        )

    return points
