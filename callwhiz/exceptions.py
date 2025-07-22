class CallWhizError(Exception):
    """Base exception for CallWhiz SDK"""
    pass


class AuthenticationError(CallWhizError):
    """Invalid API key"""
    pass


class NotFoundError(CallWhizError):
    """Resource not found"""
    pass


class RateLimitError(CallWhizError):
    """Rate limit exceeded"""
    pass