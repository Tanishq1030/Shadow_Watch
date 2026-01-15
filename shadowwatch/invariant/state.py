"""
Invariant State Module

Defines the InvariantState dataclass that holds behavioral baseline
and continuity/divergence metrics for a user.
"""

from dataclasses import dataclass, field
from typing import Optional
import numpy as np


@dataclass
class InvariantState:
    """
    Temporal identity state for a single user
    
    This is the core state object that tracks behavioral baselines
    and divergence signals. Following Document 13 specification.
    
    Attributes:
        user_id: Unique user identifier
        created_at: Unix timestamp when state was initialized
        last_seen_at: Unix timestamp of last activity
        
        baseline_vector: Mean behavioral feature vector (μ)
        baseline_variance: Variance vector (σ²) using M2 method
        sample_count: Number of observations (n)
        
        continuity_score: Current continuity C_t ∈ [0, 1]
        continuity_confidence: Confidence in score based on sample count
        
        divergence_accumulated: Ratcheting divergence D_accum
        divergence_velocity: Rate of divergence change V_t
        divergence_mode: Classification: "shock" | "creep" | "fracture" | None
    """
    
    # Identity
    user_id: str
    
    # Temporal markers
    created_at: float
    last_seen_at: float
    
    # Baseline statistics (Welford's algorithm state)
    baseline_vector: np.ndarray = field(default_factory=lambda: np.zeros(10))
    baseline_variance: np.ndarray = field(default_factory=lambda: np.zeros(10))
    sample_count: int = 0
    
    # Continuity signals
    continuity_score: float = 1.0
    continuity_confidence: float = 0.0
    
    # Divergence signals
    divergence_accumulated: float = 0.0
    divergence_velocity: float = 0.0
    divergence_mode: Optional[str] = None
    
    def to_dict(self) -> dict:
        """
        Serialize state to dictionary for database storage
        
        Returns:
            dict with JSON-compatible values
        """
        return {
            "user_id": self.user_id,
            "created_at": self.created_at,
            "last_seen_at": self.last_seen_at,
            "baseline_vector": self.baseline_vector.tolist(),
            "baseline_variance": self.baseline_variance.tolist(),
            "sample_count": self.sample_count,
            "continuity_score": float(self.continuity_score),
            "continuity_confidence": float(self.continuity_confidence),
            "divergence_accumulated": float(self.divergence_accumulated),
            "divergence_velocity": float(self.divergence_velocity),
            "divergence_mode": self.divergence_mode
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'InvariantState':
        """
        Deserialize state from database dictionary
        
        Args:
            data: Dictionary from database
            
        Returns:
            InvariantState instance
        """
        return cls(
            user_id=data["user_id"],
            created_at=data["created_at"],
            last_seen_at=data["last_seen_at"],
            baseline_vector=np.array(data["baseline_vector"]),
            baseline_variance=np.array(data["baseline_variance"]),
            sample_count=data["sample_count"],
            continuity_score=data["continuity_score"],
            continuity_confidence=data["continuity_confidence"],
            divergence_accumulated=data["divergence_accumulated"],
            divergence_velocity=data["divergence_velocity"],
            divergence_mode=data.get("divergence_mode")
        )
    
    def __repr__(self) -> str:
        """Human-readable representation"""
        return (
            f"InvariantState(user={self.user_id}, "
            f"n={self.sample_count}, "
            f"C={self.continuity_score:.3f}, "
            f"D_acc={self.divergence_accumulated:.3f}, "
            f"mode={self.divergence_mode})"
        )
