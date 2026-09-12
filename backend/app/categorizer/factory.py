"""
Factory — returns the active classifier.

To swap to a different classifier (e.g. your own ML model):
    1. Implement a class that extends BaseClassifier with a predict() method.
    2. Import it here and return an instance from get_classifier().

Nothing else in the codebase needs to change.
"""
from app.categorizer.base import BaseClassifier
from app.categorizer.rule_based import RuleBasedClassifier

# ── Swap this line to change the active classifier ──────────────────────────
_classifier: BaseClassifier = RuleBasedClassifier()
# ────────────────────────────────────────────────────────────────────────────


def get_classifier() -> BaseClassifier:
    return _classifier
