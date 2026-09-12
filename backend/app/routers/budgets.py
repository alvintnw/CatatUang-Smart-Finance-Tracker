from decimal import Decimal
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from app import models, schemas
from app.auth import get_current_user
from app.database import get_db

router = APIRouter(prefix="/api/budgets", tags=["budgets"])


def _get_spent(db: Session, user_id: int, category_id: int, month: int, year: int) -> Decimal:
    result = (
        db.query(func.coalesce(func.sum(models.Transaction.amount), 0))
        .filter(
            models.Transaction.user_id == user_id,
            models.Transaction.category_id == category_id,
            models.Transaction.type == models.TransactionType.expense,
            func.extract("month", models.Transaction.date) == month,
            func.extract("year", models.Transaction.date) == year,
        )
        .scalar()
    )
    return Decimal(str(result))


def _budget_status(spent: Decimal, limit: Decimal) -> str:
    if limit == 0:
        return "aman"
    ratio = float(spent / limit)
    if ratio >= 1.0:
        return "melewati"
    if ratio >= 0.8:
        return "mendekati"
    return "aman"


def _enrich_budget(db: Session, budget: models.Budget) -> schemas.BudgetResponse:
    spent = _get_spent(db, budget.user_id, budget.category_id, budget.month, budget.year)
    limit = Decimal(str(budget.limit_amount))
    percentage = float(spent / limit * 100) if limit > 0 else 0.0
    return schemas.BudgetResponse(
        id=budget.id,
        category=budget.category,
        month=budget.month,
        year=budget.year,
        limit_amount=limit,
        spent=spent,
        percentage=round(percentage, 1),
        status=_budget_status(spent, limit),
    )


@router.post("", response_model=schemas.BudgetResponse, status_code=201)
def create_budget(
    payload: schemas.BudgetCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    if not db.query(models.Category).filter(models.Category.id == payload.category_id).first():
        raise HTTPException(status_code=404, detail="Kategori tidak ditemukan")

    existing = (
        db.query(models.Budget)
        .filter(
            models.Budget.user_id == current_user.id,
            models.Budget.category_id == payload.category_id,
            models.Budget.month == payload.month,
            models.Budget.year == payload.year,
        )
        .first()
    )
    if existing:
        raise HTTPException(status_code=409, detail="Anggaran untuk kategori dan bulan ini sudah ada")

    budget = models.Budget(
        user_id=current_user.id,
        category_id=payload.category_id,
        month=payload.month,
        year=payload.year,
        limit_amount=payload.limit_amount,
    )
    db.add(budget)
    db.commit()
    db.refresh(budget)
    return _enrich_budget(db, budget)


@router.get("", response_model=list[schemas.BudgetResponse])
def list_budgets(
    month: Optional[int] = Query(None, ge=1, le=12),
    year: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    q = db.query(models.Budget).filter(models.Budget.user_id == current_user.id)
    if month:
        q = q.filter(models.Budget.month == month)
    if year:
        q = q.filter(models.Budget.year == year)
    budgets = q.all()
    return [_enrich_budget(db, b) for b in budgets]


@router.put("/{budget_id}", response_model=schemas.BudgetResponse)
def update_budget(
    budget_id: int,
    payload: schemas.BudgetCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    budget = (
        db.query(models.Budget)
        .filter(models.Budget.id == budget_id, models.Budget.user_id == current_user.id)
        .first()
    )
    if not budget:
        raise HTTPException(status_code=404, detail="Anggaran tidak ditemukan")
    budget.limit_amount = payload.limit_amount
    db.commit()
    db.refresh(budget)
    return _enrich_budget(db, budget)


@router.delete("/{budget_id}", status_code=204)
def delete_budget(
    budget_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    budget = (
        db.query(models.Budget)
        .filter(models.Budget.id == budget_id, models.Budget.user_id == current_user.id)
        .first()
    )
    if not budget:
        raise HTTPException(status_code=404, detail="Anggaran tidak ditemukan")
    db.delete(budget)
    db.commit()
