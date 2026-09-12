from typing import Optional
from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from app import models, schemas
from app.auth import get_current_user
from app.categorizer.factory import get_classifier
from app.database import get_db

router = APIRouter(prefix="/api/transactions", tags=["transactions"])


def _resolve_category(db: Session, slug: str) -> Optional[models.Category]:
    return db.query(models.Category).filter(models.Category.slug == slug).first()


@router.post("", response_model=schemas.TransactionResponse, status_code=201)
def create_transaction(
    payload: schemas.TransactionCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    # Auto-categorise if user didn't supply a category
    category_id = payload.category_id
    if category_id is None:
        slug = get_classifier().predict(payload.description)
        cat = _resolve_category(db, slug)
        category_id = cat.id if cat else None

    tx = models.Transaction(
        user_id=current_user.id,
        amount=payload.amount,
        type=payload.type,
        description=payload.description,
        category_id=category_id,
        date=payload.date,
        customer_name=payload.customer_name,
        payment_method=payload.payment_method,
        corrected_by_user=False,
    )
    db.add(tx)
    db.commit()
    db.refresh(tx)
    return tx


@router.get("", response_model=list[schemas.TransactionResponse])
def list_transactions(
    month: Optional[int] = Query(None, ge=1, le=12),
    year: Optional[int] = Query(None),
    type: Optional[models.TransactionType] = Query(None),
    category_id: Optional[int] = Query(None),
    limit: int = Query(50, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    q = db.query(models.Transaction).filter(models.Transaction.user_id == current_user.id)
    if month:
        q = q.filter(func.extract("month", models.Transaction.date) == month)
    if year:
        q = q.filter(func.extract("year", models.Transaction.date) == year)
    if type:
        q = q.filter(models.Transaction.type == type)
    if category_id:
        q = q.filter(models.Transaction.category_id == category_id)
    return q.order_by(models.Transaction.date.desc()).offset(offset).limit(limit).all()


@router.get("/{transaction_id}", response_model=schemas.TransactionResponse)
def get_transaction(
    transaction_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    tx = (
        db.query(models.Transaction)
        .filter(models.Transaction.id == transaction_id, models.Transaction.user_id == current_user.id)
        .first()
    )
    if not tx:
        raise HTTPException(status_code=404, detail="Transaksi tidak ditemukan")
    return tx


@router.put("/{transaction_id}", response_model=schemas.TransactionResponse)
def update_transaction(
    transaction_id: int,
    payload: schemas.TransactionUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    tx = (
        db.query(models.Transaction)
        .filter(models.Transaction.id == transaction_id, models.Transaction.user_id == current_user.id)
        .first()
    )
    if not tx:
        raise HTTPException(status_code=404, detail="Transaksi tidak ditemukan")

    update_data = payload.model_dump(exclude_unset=True)

    # If category is being manually set, mark corrected_by_user = True
    # and record it for ML training
    if "category_id" in update_data and update_data["category_id"] != tx.category_id:
        correction = models.CategoryCorrection(
            user_id=current_user.id,
            description=tx.description,
            predicted_category_id=tx.category_id,
            corrected_category_id=update_data["category_id"],
        )
        db.add(correction)
        tx.corrected_by_user = True

    for field, value in update_data.items():
        setattr(tx, field, value)

    db.commit()
    db.refresh(tx)
    return tx


@router.delete("/{transaction_id}", status_code=204)
def delete_transaction(
    transaction_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    tx = (
        db.query(models.Transaction)
        .filter(models.Transaction.id == transaction_id, models.Transaction.user_id == current_user.id)
        .first()
    )
    if not tx:
        raise HTTPException(status_code=404, detail="Transaksi tidak ditemukan")
    db.delete(tx)
    db.commit()


@router.post("/{transaction_id}/correct-category", response_model=schemas.TransactionResponse)
def correct_category(
    transaction_id: int,
    payload: schemas.CategoryCorrectionCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """Dedicated endpoint for category correction — saves training data."""
    tx = (
        db.query(models.Transaction)
        .filter(models.Transaction.id == transaction_id, models.Transaction.user_id == current_user.id)
        .first()
    )
    if not tx:
        raise HTTPException(status_code=404, detail="Transaksi tidak ditemukan")

    new_cat = db.query(models.Category).filter(models.Category.id == payload.corrected_category_id).first()
    if not new_cat:
        raise HTTPException(status_code=404, detail="Kategori tidak ditemukan")

    # Save correction for future ML training
    correction = models.CategoryCorrection(
        user_id=current_user.id,
        description=tx.description,
        predicted_category_id=tx.category_id,
        corrected_category_id=payload.corrected_category_id,
    )
    db.add(correction)

    tx.category_id = payload.corrected_category_id
    tx.corrected_by_user = True
    db.commit()
    db.refresh(tx)
    return tx
