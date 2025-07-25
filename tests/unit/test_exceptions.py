# tests/unit/test_exceptions.py - Test custom exceptions
import pytest

from src.exceptions import (
    CallWhizError,
    AuthenticationError,
    NotFoundError,
    RateLimitError
)


class TestCallWhizError:
    """Test base CallWhiz exception"""

    def test_callwhiz_error_creation(self):
        """Test creating CallWhizError"""
        error = CallWhizError("Something went wrong")
        assert str(error) == "Something went wrong"
        assert isinstance(error, Exception)

    def test_callwhiz_error_inheritance(self):
        """Test that CallWhizError is base for other errors"""
        assert issubclass(AuthenticationError, CallWhizError)
        assert issubclass(NotFoundError, CallWhizError)
        assert issubclass(RateLimitError, CallWhizError)

    def test_callwhiz_error_with_args(self):
        """Test CallWhizError with multiple arguments"""
        error = CallWhizError("Error", "with", "multiple", "args")
        assert "Error" in str(error)


class TestAuthenticationError:
    """Test authentication error"""

    def test_authentication_error_creation(self):
        """Test creating AuthenticationError"""
        error = AuthenticationError("Invalid API key")
        assert str(error) == "Invalid API key"
        assert isinstance(error, CallWhizError)
        assert isinstance(error, Exception)

    def test_authentication_error_inheritance(self):
        """Test inheritance chain"""
        error = AuthenticationError("Auth failed")
        
        # Should be instance of parent classes
        assert isinstance(error, AuthenticationError)
        assert isinstance(error, CallWhizError)
        assert isinstance(error, Exception)

    def test_authentication_error_catch(self):
        """Test catching AuthenticationError"""
        with pytest.raises(AuthenticationError) as exc_info:
            raise AuthenticationError("API key expired")
        
        assert "API key expired" in str(exc_info.value)

    def test_authentication_error_catch_as_base(self):
        """Test catching AuthenticationError as CallWhizError"""
        with pytest.raises(CallWhizError):
            raise AuthenticationError("Invalid credentials")


class TestNotFoundError:
    """Test not found error"""

    def test_not_found_error_creation(self):
        """Test creating NotFoundError"""
        error = NotFoundError("Resource not found")
        assert str(error) == "Resource not found"
        assert isinstance(error, CallWhizError)

    def test_not_found_error_inheritance(self):
        """Test inheritance chain"""
        error = NotFoundError("Agent not found")
        
        assert isinstance(error, NotFoundError)
        assert isinstance(error, CallWhizError)
        assert isinstance(error, Exception)

    def test_not_found_error_catch(self):
        """Test catching NotFoundError"""
        with pytest.raises(NotFoundError) as exc_info:
            raise NotFoundError("Agent ID 'xyz' not found")
        
        assert "Agent ID 'xyz' not found" in str(exc_info.value)


class TestRateLimitError:
    """Test rate limit error"""

    def test_rate_limit_error_creation(self):
        """Test creating RateLimitError"""
        error = RateLimitError("Rate limit exceeded")
        assert str(error) == "Rate limit exceeded"
        assert isinstance(error, CallWhizError)

    def test_rate_limit_error_inheritance(self):
        """Test inheritance chain"""
        error = RateLimitError("Too many requests")
        
        assert isinstance(error, RateLimitError)
        assert isinstance(error, CallWhizError)
        assert isinstance(error, Exception)

    def test_rate_limit_error_catch(self):
        """Test catching RateLimitError"""
        with pytest.raises(RateLimitError) as exc_info:
            raise RateLimitError("Rate limit: 100 requests per hour")
        
        assert "Rate limit: 100 requests per hour" in str(exc_info.value)


class TestExceptionHierarchy:
    """Test exception hierarchy and catching"""

    def test_catch_all_callwhiz_errors(self):
        """Test catching all CallWhiz errors with base class"""
        exceptions_to_test = [
            AuthenticationError("Auth error"),
            NotFoundError("Not found error"),
            RateLimitError("Rate limit error"),
            CallWhizError("Generic error")
        ]
        
        for exception in exceptions_to_test:
            with pytest.raises(CallWhizError):
                raise exception

    def test_catch_specific_exceptions(self):
        """Test catching specific exceptions"""
        # AuthenticationError
        with pytest.raises(AuthenticationError):
            raise AuthenticationError("Invalid API key")
        
        # NotFoundError
        with pytest.raises(NotFoundError):
            raise NotFoundError("Agent not found")
        
        # RateLimitError
        with pytest.raises(RateLimitError):
            raise RateLimitError("Rate limit exceeded")

    def test_exception_messages(self):
        """Test exception messages are preserved"""
        test_cases = [
            (CallWhizError, "Base error message"),
            (AuthenticationError, "Authentication failed"),
            (NotFoundError, "Resource not found"),
            (RateLimitError, "Too many requests")
        ]
        
        for exception_class, message in test_cases:
            error = exception_class(message)
            assert str(error) == message

    def test_exception_without_message(self):
        """Test exceptions without message"""
        exceptions = [
            CallWhizError(),
            AuthenticationError(),
            NotFoundError(),
            RateLimitError()
        ]
        
        for error in exceptions:
            # Should not raise exception when converting to string
            str(error)

    def test_multiple_inheritance_levels(self):
        """Test that we can catch exceptions at different levels"""
        auth_error = AuthenticationError("Invalid key")
        
        # Can catch as specific type
        try:
            raise auth_error
        except AuthenticationError:
            pass
        else:
            pytest.fail("Should have caught AuthenticationError")
        
        # Can catch as base CallWhiz error
        try:
            raise auth_error
        except CallWhizError:
            pass
        else:
            pytest.fail("Should have caught CallWhizError")
        
        # Can catch as generic Exception
        try:
            raise auth_error
        except Exception:
            pass
        else:
            pytest.fail("Should have caught Exception")

    def test_re_raising_exceptions(self):
        """Test re-raising exceptions maintains type"""
        def inner_function():
            raise AuthenticationError("Original error")
        
        def outer_function():
            try:
                inner_function()
            except CallWhizError as e:
                # Re-raise the same exception
                raise e
        
        # Should maintain original exception type
        with pytest.raises(AuthenticationError) as exc_info:
            outer_function()
        
        assert "Original error" in str(exc_info.value)

    def test_exception_args_preserved(self):
        """Test that exception args are preserved"""
        error = CallWhizError("arg1", "arg2", "arg3")
        assert error.args == ("arg1", "arg2", "arg3")
        
        auth_error = AuthenticationError("auth_arg1", "auth_arg2")
        assert auth_error.args == ("auth_arg1", "auth_arg2")