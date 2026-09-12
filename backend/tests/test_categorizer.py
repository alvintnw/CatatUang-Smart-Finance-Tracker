"""Tests for the rule-based categorizer — no DB required."""
import pytest

from app.categorizer.rule_based import RuleBasedClassifier

clf = RuleBasedClassifier()


@pytest.mark.parametrize(
    "description,expected_slug",
    [
        ("beli kopi starbucks 45rb", "makanan"),
        ("makan siang warteg 15k", "makanan"),
        ("bayar listrik pln 250rb", "tagihan"),
        ("bayar internet indihome", "tagihan"),
        ("gojek ke kampus", "transportasi"),
        ("bensin motor pertamina", "transportasi"),
        ("beli sepatu shopee", "belanja"),
        ("netflix bulan ini", "hiburan"),
        ("bioskop cgv jumat malem", "hiburan"),
        ("bayar spp kuliah", "pendidikan"),
        ("obat dari apotek", "kesehatan"),
        ("transfer gaji dari kantor", "gaji"),
        ("random pengeluaran tanpa keterangan", "lain-lain"),
    ],
)
def test_categorizer_predictions(description, expected_slug):
    assert clf.predict(description) == expected_slug


def test_categorizer_case_insensitive():
    assert clf.predict("BELI KOPI STARBUCKS") == "makanan"


def test_categorizer_returns_lain_lain_for_empty():
    assert clf.predict("") == "lain-lain"
