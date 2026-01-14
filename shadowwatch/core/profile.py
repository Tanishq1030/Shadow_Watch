"""
Profile Engine - FREE TIER

Handles user profile generation and retrieval.
"""
from typing import Dict, List


class ProfileEngine:
    """
    User profile engine - FREE TIER
    
    Responsibilities:
    - Generate user profile
    - Include statistics
    - Optionally include activities
    
    No license required. This is a core free tier feature.
    """
    
    def __init__(self, library_engine):
        """
        Initialize profile engine
        
        Args:
            library_engine: LibraryEngine instance (for profile data)
        """
        self.library_engine = library_engine
    
    async def get(
        self,
        user_id: int,
        include_activities: bool = False
    ) -> Dict:
        """
        Get user's behavioral profile
        
        Args:
            user_id: User identifier
            include_activities: Whether to include activity log
        
        Returns:
            {
                "user_id": int,
                "library": List[Dict],
                "total_activities": int,
                "pinned_count": int,
                "fingerprint": str,
                "activities": List[Dict] (optional)
            }
        """
        # Get library data (which includes all the profile info)
        library_data = await self.library_engine.get(user_id)
        
        # Profile is essentially the library data with user_id
        profile = {
            "user_id": user_id,
            **library_data
        }
        
        # Optionally include activities (not implemented yet in free tier)
        if include_activities:
            # TODO: Add activity retrieval in future
            profile["activities"] = []
        
        return profile
