"""
FastAPI Middleware for Shadow Watch

Automatically tracks user activity on FastAPI routes
"""

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Callable, Optional


class ShadowWatchMiddleware(BaseHTTPMiddleware):
    """
    FastAPI middleware for automatic activity tracking
    
    Usage:
        from shadowwatch import ShadowWatch
        from shadowwatch.integrations.fastapi import ShadowWatchMiddleware
        
        app = FastAPI()
        sw = ShadowWatch(database_url="...")
        
        app.add_middleware(
            ShadowWatchMiddleware,
            shadow_watch=sw,
            user_id_getter=lambda request: request.state.user.id,
            entity_extractor=extract_symbol_from_path
        )
    """
    
    def __init__(
        self,
        app,
        shadow_watch,
        user_id_getter: Callable[[Request], Optional[int]],
        entity_extractor: Optional[Callable[[Request], Optional[str]]] = None,
        action_mapper: Optional[Callable[[Request], str]] = None
    ):
        """
        Initialize Shadow Watch middleware
        
        Args:
            app: FastAPI application
            shadow_watch: ShadowWatch instance
            user_id_getter: Function to extract user_id from request
                           Example: lambda req: req.state.user.id
            entity_extractor: Optional function to extract entity ID from request
                            Example: lambda req: req.path_params.get('symbol')
            action_mapper: Optional function to map HTTP method to action type
                          Default: GET=view, POST=trade, etc.
        """
        super().__init__(app)
        self.shadow_watch = shadow_watch
        self.user_id_getter = user_id_getter
        self.entity_extractor = entity_extractor or self._default_entity_extractor
        self.action_mapper = action_mapper or self._default_action_mapper
    
    def _default_entity_extractor(self, request: Request) -> Optional[str]:
        """
        Default entity extraction: try to pull a generic identifier from the request.
        
        Priority:
        1) Path params (slug/id/entity_id/resource_id/item_id/symbol/ticker/asset)
        2) Query params with similar keys
        3) Last path segment for REST-style routes (e.g., /articles/quantum-computing)
        """
        path = request.url.path
        
        # Try to extract from path params first
        if hasattr(request, 'path_params'):
            for key in ['entity_id', 'slug', 'id', 'item_id', 'resource_id', 'symbol', 'ticker', 'asset']:
                if key in request.path_params:
                    return request.path_params[key]
        
        # Query params fallback
        if hasattr(request, "query_params"):
            for key in ['entity_id', 'slug', 'id', 'item_id', 'resource_id', 'symbol', 'ticker', 'asset']:
                if key in request.query_params:
                    return request.query_params.get(key)
        
        # Fallback: use the last path segment if available and not empty
        segments = [seg for seg in path.split("/") if seg]
        if len(segments) >= 2:
            candidate = segments[-1]
            if 0 < len(candidate) <= 100:
                return candidate
        
        return None
    
    def _default_action_mapper(self, request: Request) -> str:
        """
        Default action mapping based on HTTP method and path
        
        Designed to be domain-agnostic:
        - GET -> view
        - POST -> create (unless search/trade/watchlist/alert patterns detected)
        - PUT/PATCH -> update
        - DELETE -> delete
        """
        method = request.method
        path = request.url.path.lower()
        
        if method == "GET":
            return "view"
        elif method == "POST":
            if "trade" in path or "order" in path or "buy" in path or "sell" in path:
                return "trade"
            elif "search" in path:
                return "search"
            elif "watchlist" in path:
                return "watchlist_add"
            elif "alert" in path:
                return "alert_set"
            else:
                return "create"
        elif method in {"PUT", "PATCH"}:
            return "update"
        elif method == "DELETE":
            return "delete"
        else:
            return "view"
    
    async def dispatch(self, request: Request, call_next):
        """Process request and track activity if applicable"""
        
        # Process the request first
        response = await call_next(request)
        
        # Only track successful responses
        if response.status_code >= 400:
            return response
        
        try:
            # Extract user ID
            user_id = self.user_id_getter(request)
            if not user_id:
                return response
            
            # Extract entity ID
            entity_id = self.entity_extractor(request)
            if not entity_id:
                return response
            
            # Determine action type
            action = self.action_mapper(request)
            
            # Track activity (silent, async)
            await self.shadow_watch.track(
                user_id=user_id,
                entity_id=entity_id,
                action=action,
                metadata={
                    "path": str(request.url.path),
                    "method": request.method
                }
            )
        
        except Exception as e:
            # Silent fail - don't break request if tracking fails
            print(f"⚠️ Shadow Watch tracking failed: {e}")
        
        return response


# Convenience function for simple setup
def add_shadow_watch(
    app,
    shadow_watch,
    user_id_getter: Callable[[Request], Optional[int]]
):
    """
    Quick setup: Add Shadow Watch middleware to FastAPI app
    
    Usage:
        from shadowwatch.integrations.fastapi import add_shadow_watch
        
        add_shadow_watch(
            app,
            shadow_watch=sw,
            user_id_getter=lambda req: req.state.user.id
        )
    """
    app.add_middleware(
        ShadowWatchMiddleware,
        shadow_watch=shadow_watch,
        user_id_getter=user_id_getter
    )
