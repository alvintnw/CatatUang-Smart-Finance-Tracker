"""
Categorizer interface.

To swap in a different classifier (ML, LLM, etc.):
1. Create a new class that inherits from BaseClassifier
2. Override the `predict` method
3. Change the `get_classifier()` factory to return your new class

That's it — no other code needs to change.
"""
from abc import ABC, abstractmethod


class BaseClassifier(ABC):
    """
    Abstract base for all category classifiers.

    predict(description: str) -> str
        Returns a category slug (e.g. "makanan", "transportasi").
        The slug must match an existing Category.slug in the database.
        Return "lain-lain" when uncertain.
    """

    @abstractmethod
    def predict(self, description: str) -> str:
        ...
