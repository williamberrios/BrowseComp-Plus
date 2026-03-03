"""
Searchers package for different search implementations.
"""

from enum import Enum

from .base import BaseSearcher


def _load_bm25():
    from .bm25_searcher import BM25Searcher
    return BM25Searcher


def _load_faiss():
    from .faiss_searcher import FaissSearcher
    return FaissSearcher


def _load_reasonir():
    from .faiss_searcher import ReasonIrSearcher
    return ReasonIrSearcher


def _load_custom():
    from .custom_searcher import CustomSearcher
    return CustomSearcher


class SearcherType(Enum):
    """Enum for managing available searcher types and their CLI mappings."""

    BM25 = ("bm25", _load_bm25)
    FAISS = ("faiss", _load_faiss)
    REASONIR = ("reasonir", _load_reasonir)
    CUSTOM = ("custom", _load_custom)  # Your custom searcher class, yet to be implemented

    def __init__(self, cli_name, searcher_class):
        self.cli_name = cli_name
        self.searcher_class = searcher_class

    @classmethod
    def get_choices(cls):
        """Get list of CLI choices for argument parser."""
        return [searcher_type.cli_name for searcher_type in cls]

    @classmethod
    def get_searcher_class(cls, cli_name):
        """Get searcher class by CLI name."""
        for searcher_type in cls:
            if searcher_type.cli_name == cli_name:
                return searcher_type.searcher_class()  # call loader to import on demand
        raise ValueError(f"Unknown searcher type: {cli_name}")


__all__ = ["BaseSearcher", "SearcherType"]
