"""
Shadow Watch Exceptions
"""

class LicenseError(Exception):
    """
    Raised when Pro features are accessed without valid license
    """
    pass


class LocalDevLimitError(Exception):
    """
    Raised when local dev mode event limit is reached (deprecated)
    
    This exception is kept for backward compatibility but will be removed
    in future versions. Free tier now has no event limits.
    """
    pass
