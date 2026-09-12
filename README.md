# 💰 CatatUang

Aplikasi web manajemen keuangan sederhana untuk **mahasiswa** dan **pelaku UMKM kecil** di Indonesia.
Fitur utama: pencatatan transaksi cepat, kategorisasi otomatis dari teks deskripsi, dashboard insight bulanan, manajemen anggaran, dan ekspor laporan.

---

## Fitur

| Fitur | Keterangan |
|---|---|
| ✅ Pencatatan transaksi | Input manual cepat dengan auto-kategorisasi |
| ✅ Kategorisasi otomatis | Rule-based keyword matching (mudah diganti ML) |
| ✅ Koreksi kategori | User koreksi → disimpan sebagai data latih ML |
| ✅ Dashboard insight | Ringkasan, pie chart, line chart tren, insight teks |
| ✅ Mode UMKM | Field pelanggan/supplier + metode pembayaran |
| ✅ Manajemen anggaran | Target per kategori per bulan + progress bar |
| ✅ Ekspor | CSV dan Excel (.xlsx) |
| ✅ Autentikasi | Email/password + JWT |

---

## Arsitektur

```
catatuang/
├── backend/              # FastAPI + PostgreSQL
│   ├── app/
│   │   ├── categorizer/  # ← modul kategorisasi (pluggable)
│   │   │   ├── base.py       # interface BaseClassifier
│   │   │   ├── rule_based.py # implementasi rule-based (default)
│   │   │   └── factory.py    # ← ganti classifier di sini
│   │   ├── routers/
│   │   │   ├── auth.py
│   │   │   ├── transactions.py
│   │   │   ├── budgets.py
│   │   │   ├── dashboard.py
│   │   │   └── export.py
│   │   ├── models.py
│   │   ├── schemas.py
│   │   ├── auth.py
│   │   └── main.py
│   ├── alembic/          # migrasi database
│   ├── tests/            # pytest
│   └── requirements.txt
└── frontend/             # React + Tailwind + Recharts
    └── src/
        ├── pages/        # DashboardPage, TransactionsPage, BudgetsPage
        ├── components/   # TransactionForm, Layout, ExportButtons, …
        ├── contexts/     # AuthContext
        └── lib/          # api.js (axios), utils.js
```

---

## Cara Mengganti Classifier Kategorisasi

> Ini dirancang agar kamu bisa plug-in model ML kamu sendiri **tanpa mengubah** kode lain.

1. Buat class baru di `backend/app/categorizer/`:

```python
# backend/app/categorizer/my_ml_classifier.py
from app.categorizer.base import BaseClassifier

class MyMLClassifier(BaseClassifier):
    def __init__(self):
        # load model kamu di sini
        self.model = ...

    def predict(self, description: str) -> str:
        # return slug kategori, e.g. "makanan", "transportasi"
        return self.model.predict([description])[0]
```

2. Edit `factory.py` — hanya **satu baris**:

```python
# from app.categorizer.rule_based import RuleBasedClassifier
# _classifier = RuleBasedClassifier()

from app.categorizer.my_ml_classifier import MyMLClassifier
_classifier = MyMLClassifier()
```

Data koreksi tersimpan di tabel `category_corrections` — export dengan:
```sql
SELECT description, c.slug AS corrected_slug
FROM category_corrections cc
JOIN categories c ON c.id = cc.corrected_category_id;
```

---

## Setup Lokal

### Prasyarat

- Python 3.11+
- Node.js 18+
- PostgreSQL 14+

### 1. Clone & Persiapan

```bash
git clone <repo-url>
cd catatuang
```

### 2. Backend

```bash
cd backend

# Buat virtual environment
python -m venv venv
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependensi
pip install -r requirements.txt
```

**Buat file `.env`** di folder `backend/`:

```env
DATABASE_URL=postgresql://postgres:password@localhost:5432/catatuang
SECRET_KEY=ganti-dengan-secret-key-yang-kuat
```

**Setup database:**

```bash
# Buat database PostgreSQL
createdb catatuang

# Jalankan migrasi
alembic upgrade head
```

**Jalankan backend:**

```bash
uvicorn app.main:app --reload --port 8000
```

API tersedia di: `http://localhost:8000`  
Dokumentasi interaktif (Swagger): `http://localhost:8000/docs`

### 3. Frontend

```bash
cd ../frontend

# Install dependensi
npm install

# Jalankan dev server
npm run dev
```

Aplikasi tersedia di: `http://localhost:5173`

> **Catatan:** Vite sudah dikonfigurasi untuk mem-proxy `/api/*` ke `http://localhost:8000`, sehingga tidak perlu konfigurasi CORS tambahan untuk development.

---

## Menjalankan Tests

```bash
cd backend

# Install test dependencies (sudah ada di requirements.txt)
# Tests menggunakan SQLite in-memory — tidak perlu PostgreSQL berjalan

pytest -v
```

Output yang diharapkan:
```
tests/test_auth.py::test_register            PASSED
tests/test_auth.py::test_login_success       PASSED
tests/test_transactions.py::test_create_...  PASSED
tests/test_categorizer.py::test_categori...  PASSED
... dst
```

---

## Endpoint API Utama

| Method | Endpoint | Keterangan |
|---|---|---|
| POST | `/api/auth/register` | Registrasi akun baru |
| POST | `/api/auth/login` | Login, return JWT token |
| GET | `/api/auth/me` | Info user saat ini |
| POST | `/api/transactions` | Catat transaksi baru |
| GET | `/api/transactions` | List transaksi (filter bulan/tahun/tipe) |
| PUT | `/api/transactions/{id}` | Edit transaksi |
| DELETE | `/api/transactions/{id}` | Hapus transaksi |
| POST | `/api/transactions/{id}/correct-category` | Koreksi kategori + simpan data latih |
| GET | `/api/categories` | List semua kategori |
| POST | `/api/budgets` | Tambah anggaran |
| GET | `/api/budgets` | List anggaran dengan progress |
| GET | `/api/dashboard/summary` | Ringkasan bulan + insight |
| GET | `/api/dashboard/trend` | Tren 6 bulan terakhir |
| GET | `/api/export/csv` | Export CSV |
| GET | `/api/export/excel` | Export Excel |

---

## Tech Stack

| Layer | Teknologi |
|---|---|
| Backend | Python 3.11, FastAPI, SQLAlchemy 2, Alembic |
| Database | PostgreSQL 14+ |
| Auth | JWT (python-jose), bcrypt (passlib) |
| Frontend | React 18, Vite, Tailwind CSS 3, Recharts |
| Testing | pytest, httpx (FastAPI TestClient) |
| Export | pandas, openpyxl |

---

## Kategori Default

| Slug | Nama | Contoh kata kunci |
|---|---|---|
| `makanan` | Makanan & Minuman | kopi, makan, warteg, starbucks |
| `transportasi` | Transportasi | gojek, grab, bensin, krl |
| `tagihan` | Tagihan & Utilitas | listrik, pln, internet, kos |
| `belanja` | Belanja | shopee, tokopedia, baju, sepatu |
| `hiburan` | Hiburan | netflix, bioskop, game |
| `pendidikan` | Pendidikan | spp, buku, kursus, les |
| `kesehatan` | Kesehatan | dokter, apotek, obat |
| `gaji` | Gaji & Pendapatan | gaji, honor, freelance |
| `lain-lain` | Lain-lain | (fallback) |

---

## Pengembangan Selanjutnya

- [ ] Ganti `RuleBasedClassifier` dengan model ML (lihat bagian **Cara Mengganti Classifier**)
- [ ] Notifikasi push / email saat anggaran mendekati batas
- [ ] Multi-currency support
- [ ] Foto/scan struk (OCR → deskripsi otomatis)
- [ ] Laporan bulanan PDF
- [ ] PWA (installable di mobile)
