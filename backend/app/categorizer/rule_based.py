"""
Rule-based keyword classifier.

Logic: iterate over ordered rules (most-specific first); return the slug of
the first rule whose keywords appear in the normalised description.

This module is intentionally kept simple so it can be replaced with an ML
model by swapping the classifier returned from get_classifier() in factory.py.

Adding or tuning rules: edit RULES below. Each entry is a tuple of
(slug, [keywords...]).  Keywords are matched as substrings after lowercasing
and stripping Indonesian number suffixes (rb, k, jt).
"""

import re
from typing import List, Tuple

from app.categorizer.base import BaseClassifier

# ---------------------------------------------------------------------------
# Rule definitions — (slug, keywords)
# Order matters: first match wins.
# ---------------------------------------------------------------------------
RULES: List[Tuple[str, List[str]]] = [
    # --- Makanan & Minuman ---
    (
        "makanan",
        [
            "makan", "minum", "kopi", "coffee", "teh", "susu", "jus", "juice",
            "nasi", "mie", "bakso", "soto", "warung", "restoran", "resto",
            "cafe", "kaffe", "starbucks", "mcdonalds", "kfc", "pizza",
            "burger", "ayam", "sate", "gado", "warteg", "lalapan",
            "gorengan", "snack", "cemilan", "indomaret", "alfamart",
            "minimarket", "supermarket", "groceries", "bahan makanan",
            "sembako", "beras", "sayur", "buah", "daging",
        ],
    ),
    # --- Transportasi ---
    (
        "transportasi",
        [
            "gojek", "grab", "ojek", "taxi", "taksi", "angkot", "bus",
            "busway", "transjakarta", "mrt", "krl", "kereta", "bensin",
            "bbm", "pertamina", "spbu", "parkir", "tol", "uber", "maxim",
            "indriver", "motor", "mobil", "bahan bakar",
        ],
    ),
    # --- Tagihan & Utilitas ---
    (
        "tagihan",
        [
            "listrik", "air", "pdam", "pln", "internet", "wifi", "indihome",
            "myrepublic", "firstmedia", "tv kabel", "bpjs", "asuransi",
            "premi", "sewa", "kontrakan", "kos", "kost", "bayar listrik",
            "bayar air", "iuran", "cicilan", "kredit", "angsuran",
            "telepon", "pulsa", "paket data", "xl", "telkomsel", "indosat",
            "by.u", "smartfren",
        ],
    ),
    # --- Pendidikan ---
    (
        "pendidikan",
        [
            "spp", "ukt", "kuliah", "sekolah", "kursus", "les", "buku",
            "buku teks", "fotokopi", "print", "ujian", "seminar", "workshop",
            "pelatihan", "training", "udemy", "coursera", "ruangguru",
            "zenius", "alat tulis", "atk", "skripsi", "tesis",
        ],
    ),
    # --- Kesehatan ---
    (
        "kesehatan",
        [
            "dokter", "rumah sakit", "rs", "klinik", "puskesmas", "apotek",
            "obat", "vitamin", "suplemen", "cek kesehatan", "lab", "rontgen",
            "gigi", "optik", "kacamata", "gym", "fitnes", "fitness",
        ],
    ),
    # --- Hiburan ---
    (
        "hiburan",
        [
            "netflix", "spotify", "youtube", "streaming", "bioskop",
            "cinema", "cgv", "xxi", "game", "steam", "playstation",
            "xbox", "konser", "tiket", "wisata", "liburan", "hotel",
            "airbnb", "karaoke", "bowling",
        ],
    ),
    # --- Belanja ---
    (
        "belanja",
        [
            "shopee", "tokopedia", "lazada", "bukalapak", "blibli", "tiktok shop",
            "baju", "celana", "sepatu", "sandal", "tas", "dompet",
            "fashion", "pakaian", "aksesoris", "kosmetik", "skincare",
            "perabot", "elektronik", "gadget", "hp", "laptop",
        ],
    ),
    # --- Gaji & Pendapatan ---
    (
        "gaji",
        [
            "gaji", "salary", "honor", "honorarium", "thr", "bonus",
            "freelance", "proyek", "project fee", "transfer masuk",
            "uang masuk", "pendapatan", "omzet", "penjualan",
            "pembayaran pelanggan",
        ],
    ),
]


def _normalize(text: str) -> str:
    """Lowercase, remove currency markers and Indonesian shorthand (rb=ribu, k=ribu, jt=juta)."""
    text = text.lower()
    text = re.sub(r"\b\d+\s*(rb|k|ribu|jt|juta|rp\.?)\b", " ", text)
    text = re.sub(r"[^\w\s]", " ", text)
    return text


class RuleBasedClassifier(BaseClassifier):
    """Simple keyword-matching classifier."""

    def predict(self, description: str) -> str:
        normalised = _normalize(description)
        for slug, keywords in RULES:
            if any(kw in normalised for kw in keywords):
                return slug
        return "lain-lain"
