"""Independent ingestion subsystem: discovery adapters and shared contracts.

Import this package without importing ranking, clustering, publication or AI code.
All adapters emit observations, never validated news items.
"""
from .contracts import observation, canonical_url_hint

__all__ = ["observation", "canonical_url_hint"]
