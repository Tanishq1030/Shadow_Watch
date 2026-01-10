"""Shadow Watch core functionality"""

from shadowwatch.core.tracker import track_activity
from shadowwatch.core.scorer import generate_library_snapshot
from shadowwatch.core.fingerprint import verify_fingerprint
from shadowwatch.core.trust_score import calculate_trust_score
from shadowwatch.core.pruner import smart_prune_if_needed

__all__ = [
    "track_activity",
    "generate_library_snapshot",
    "verify_fingerprint",
    "calculate_trust_score",
    "smart_prune_if_needed"
]
