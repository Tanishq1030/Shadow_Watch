"""
Library Generation & Interest Scoring

Thin wrapper around library.py for backward compatibility.
"""
from shadowwatch.core.library import generate_library_snapshot

__all__ = ["generate_library_snapshot"]
