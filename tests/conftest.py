# tests/conftest.py - Pytest configuration and fixtures
import pytest
from datetime import datetime
from unittest.mock import Mock, MagicMock
import httpx
import respx

# Import your SDK components
from callwhiz.client import CallWhiz
from callwhiz.models import Agent, Call
from callwhiz.exceptions import CallWhizError, AuthenticationError, NotFoundError


# Test data fixtures
@pytest.fixture
def sample_voice_config():
    """Sample voice configuration"""
    return {
        "provider": "openai",
        "voice_id": "alloy",
        "speed": 1.0,
        "pitch": 1.0
    }


@pytest.fixture
def sample_llm_config():
    """Sample LLM configuration"""
    return {
        "provider": "openai",
        "model": "gpt-4",
        "temperature": 0.7,
        "max_tokens": 150
    }


@pytest.fixture
def sample_agent_settings():
    """Sample agent settings"""
    return {
        "max_call_duration": 1800,
        "enable_interruptions": True,
        "silence_timeout": 5,
        "response_delay": 0.5
    }


@pytest.fixture
def sample_agent_data(sample_voice_config, sample_llm_config, sample_agent_settings):
    """Sample agent data for API responses"""
    return {
        "id": "agent_123",
        "name": "Test Agent",
        "description": "Test agent description",
        "status": "active",
        "created_at": "2024-01-01T10:00:00Z",
        "updated_at": "2024-01-01T10:00:00Z",
        "voice": sample_voice_config,
        "llm": sample_llm_config,
        "settings": sample_agent_settings,
        "prompt": "You are a helpful assistant",
        "first_message": "Hello!",
        "call_count": 0,
        "total_duration": 0
    }


@pytest.fixture
def sample_call_data():
    """Sample call data for API responses"""
    return {
        "call_id": "call_123",
        "status": "initiated",
        "agent_id": "agent_123",
        "phone_number": "+1234567890",
        "created_at": "2024-01-01T10:00:00Z",
        "estimated_cost": 0.05,
        "context": {"customer_name": "John Doe"},
        "metadata": {"test": True}
    }


@pytest.fixture
def sample_webhook_data():
    """Sample webhook data for API responses"""
    return {
        "webhook_id": "webhook_123",
        "url": "https://example.com/webhook",
        "events": ["call.started", "call.completed"],
        "agent_ids": ["agent_123"],
        "active": True,
        "created_at": "2024-01-01T10:00:00Z",
        "secret": "whsec_test123"
    }


@pytest.fixture
def api_key():
    """Test API key"""
    return "cw_test_123456789"


@pytest.fixture
def base_url():
    """Test base URL"""
    return "http://localhost:8000/v1/api/developer/v1"


@pytest.fixture
def mock_success_response():
    """Mock successful API response"""
    def _create_response(data):
        return {
            "success": True,
            "data": data
        }
    return _create_response


@pytest.fixture
def mock_error_response():
    """Mock error API response"""
    def _create_error(code, message, details=None):
        return {
            "success": False,
            "error": {
                "code": code,
                "message": message,
                "details": details or {}
            }
        }
    return _create_error


@pytest.fixture
def callwhiz_client(api_key):
    """CallWhiz client instance for testing"""
    return CallWhiz(api_key=api_key, sandbox=True)


@pytest.fixture
def mock_http_client():
    """Mock HTTP client"""
    client = Mock(spec=httpx.Client)
    client.request = Mock()
    client.close = Mock()
    return client


# Respx fixtures for HTTP mocking
@pytest.fixture
def respx_mock():
    """Respx mock for HTTP requests"""
    with respx.mock() as mock:
        yield mock


@pytest.fixture
def mock_agents_endpoint(respx_mock, base_url, mock_success_response, sample_agent_data):
    """Mock agents API endpoints"""
    # GET /agents - list agents
    respx_mock.get(f"{base_url}/agents").mock(
        return_value=httpx.Response(200, json=mock_success_response([sample_agent_data]))
    )
    
    # POST /agents - create agent
    respx_mock.post(f"{base_url}/agents").mock(
        return_value=httpx.Response(200, json=mock_success_response(sample_agent_data))
    )
    
    # GET /agents/{id} - get agent
    respx_mock.get(f"{base_url}/agents/agent_123").mock(
        return_value=httpx.Response(200, json=mock_success_response(sample_agent_data))
    )
    
    # PUT /agents/{id} - update agent
    respx_mock.put(f"{base_url}/agents/agent_123").mock(
        return_value=httpx.Response(200, json=mock_success_response(sample_agent_data))
    )
    
    # DELETE /agents/{id} - delete agent
    respx_mock.delete(f"{base_url}/agents/agent_123").mock(
        return_value=httpx.Response(200, json=mock_success_response({"message": "Agent deleted"}))
    )


@pytest.fixture
def mock_calls_endpoint(respx_mock, base_url, mock_success_response, sample_call_data):
    """Mock calls API endpoints"""
    # POST /calls - start call
    respx_mock.post(f"{base_url}/calls").mock(
        return_value=httpx.Response(200, json=mock_success_response(sample_call_data))
    )
    
    # GET /calls - list calls
    respx_mock.get(f"{base_url}/calls").mock(
        return_value=httpx.Response(200, json=mock_success_response([sample_call_data]))
    )
    
    # GET /calls/{id} - get call
    respx_mock.get(f"{base_url}/calls/call_123").mock(
        return_value=httpx.Response(200, json=mock_success_response(sample_call_data))
    )


@pytest.fixture
def mock_webhooks_endpoint(respx_mock, base_url, mock_success_response, sample_webhook_data):
    """Mock webhooks API endpoints"""
    # POST /webhooks - create webhook
    respx_mock.post(f"{base_url}/webhooks").mock(
        return_value=httpx.Response(200, json=mock_success_response(sample_webhook_data))
    )
    
    # GET /webhooks - list webhooks
    respx_mock.get(f"{base_url}/webhooks").mock(
        return_value=httpx.Response(200, json=mock_success_response([sample_webhook_data]))
    )


@pytest.fixture
def mock_error_endpoints(respx_mock, base_url, mock_error_response):
    """Mock error responses"""
    # 401 Unauthorized
    respx_mock.get(f"{base_url}/unauthorized").mock(
        return_value=httpx.Response(401, json=mock_error_response("UNAUTHORIZED", "Invalid API key"))
    )
    
    # 404 Not Found
    respx_mock.get(f"{base_url}/notfound").mock(
        return_value=httpx.Response(404, json=mock_error_response("NOT_FOUND", "Resource not found"))
    )
    
    # 429 Rate Limited
    respx_mock.get(f"{base_url}/ratelimited").mock(
        return_value=httpx.Response(429, json=mock_error_response("RATE_LIMITED", "Rate limit exceeded"))
    )


# Test helpers
def assert_agent_equal(agent1: Agent, agent2: dict):
    """Helper to compare Agent object with dict data"""
    assert agent1.id == agent2["id"]
    assert agent1.name == agent2["name"]
    assert agent1.status == agent2["status"]
    assert agent1.voice.provider == agent2["voice"]["provider"]
    assert agent1.llm.provider == agent2["llm"]["provider"]


def assert_call_equal(call1: Call, call2: dict):
    """Helper to compare Call object with dict data"""
    assert call1.call_id == call2["call_id"]
    assert call1.status == call2["status"]
    assert call1.agent_id == call2["agent_id"]
    assert call1.phone_number == call2["phone_number"]