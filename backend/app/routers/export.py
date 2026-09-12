import io
from datetime import date
from typing import Optional

import pandas as pd
from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app import models
from app.auth import get_current_user
from app.database import get_db

router = APIRouter(prefix="/api/export", tags=["export"])


def _build_dataframe(transactions: list[models.Transaction]) -> pd.DataFrame:
    rows = []
    for tx in transactions:
        rows.append(
            {
                "ID": tx.id,
                "Tanggal": tx.date.strftime("%d/%m/%Y"),
                "Tipe": "Pemasukan" if tx.type == models.TransactionType.income else "Pengeluaran",
                "Deskripsi": tx.description,
                "Kategori": tx.category.name if tx.category else "—",
                "Nominal (Rp)": float(tx.amount),
                "Pelanggan/Supplier": tx.customer_name or "",
                "Metode Pembayaran": tx.payment_method.value if tx.payment_method else "",
            }
        )
    return pd.DataFrame(rows)


@router.get("/csv")
def export_csv(
    month: Optional[int] = Query(None, ge=1, le=12),
    year: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    q = db.query(models.Transaction).filter(models.Transaction.user_id == current_user.id)
    if month:
        from sqlalchemy import func
        q = q.filter(func.extract("month", models.Transaction.date) == month)
    if year:
        from sqlalchemy import func
        q = q.filter(func.extract("year", models.Transaction.date) == year)

    transactions = q.order_by(models.Transaction.date.asc()).all()
    df = _build_dataframe(transactions)

    stream = io.StringIO()
    df.to_csv(stream, index=False)
    stream.seek(0)

    filename = f"transaksi_{month or 'all'}_{year or date.today().year}.csv"
    return StreamingResponse(
        iter([stream.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )


@router.get("/excel")
def export_excel(
    month: Optional[int] = Query(None, ge=1, le=12),
    year: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    from sqlalchemy import func

    q = db.query(models.Transaction).filter(models.Transaction.user_id == current_user.id)
    if month:
        q = q.filter(func.extract("month", models.Transaction.date) == month)
    if year:
        q = q.filter(func.extract("year", models.Transaction.date) == year)

    transactions = q.order_by(models.Transaction.date.asc()).all()
    df = _build_dataframe(transactions)

    stream = io.BytesIO()
    with pd.ExcelWriter(stream, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Transaksi")
    stream.seek(0)

    filename = f"transaksi_{month or 'all'}_{year or date.today().year}.xlsx"
    return StreamingResponse(
        iter([stream.getvalue()]),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )
