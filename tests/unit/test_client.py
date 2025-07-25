# tests/unit/test_client.py - Test CallWhiz client
import pytest
import httpx
import respx
from unittest.mock import Mock, patch

from src.client import CallWhiz
from src.models import Agent, Call, Webhook
from src.exceptions import CallWhizError, AuthenticationError, NotFoundError, RateLimitError


class TestCallWhizClient:
    """Test CallWhiz client initialization and basic functionality"""

    def test_client_initialization(self):
        """Test client initialization with valid API key"""
        client = CallWhiz(api_key="cw_test_123", sandbox=True)
        
        assert client.api_key == "cw_test_123"
        assert "sandbox" in client.base_url or "localhost" in client.base_url
        assert client.session.headers["X-API-Key"] == "cw_test_123"
        assert client.session.headers["Content-Type"] == "application/json"

    def test_client_initialization_no_api_key(self):
        """Test client initialization without API key"""
        with pytest.raises(ValueError, match="API key is required"):
            CallWhiz(api_key="")

        with pytest.raises(ValueError, match="API key is required"):
            CallWhiz(api_key=None)

    def test_client_production_mode(self):
        """Test client in production mode"""
        client = CallWhiz(api_key="cw_live_123", sandbox=False)
        
        # Should not contain sandbox in URL
        assert "sandbox" not in client.base_url

    def test_client_context_manager(self):
        """Test client as context manager"""
        with CallWhiz(api_key="cw_test_123") as client:
            assert client.api_key == "cw_test_123"
        
        # Session should be closed after context
        assert client.session.is_closed

    def test_client_close(self):
        """Test manual client close"""
        client = CallWhiz(api_key="cw_test_123")
        assert not client.session.is_closed
        
        client.close()
        assert client.session.is_closed


class TestClientErrorHandling:
    """Test client error handling and HTTP status codes"""

    def test_401_authentication_error(self, respx_mock, base_url):
        """Test 401 Unauthorized handling"""
        respx_mock.get(f"{base_url}/test").mock(
            return_value=httpx.Response(401, json={"error": "Unauthorized"})
        )
        
        client = CallWhiz(api_key="invalid_key", sandbox=True)
        
        with pytest.raises(AuthenticationError, match="Invalid API key"):
            client._request("GET", "/test")

    def test_404_not_found_error(self, respx_mock, base_url):
        """Test 404 Not Found handling"""
        respx_mock.get(f"{base_url}/test").mock(
            return_value=httpx.Response(404, json={"error": "Not found"})
        )
        
        client = CallWhiz(api_key="cw_test_123", sandbox=True)
        
        with pytest.raises(NotFoundError, match="Resource not found"):
            client._request("GET", "/test")

    def test_429_rate_limit_error(self, respx_mock, base_url):
        """Test 429 Rate Limited handling"""
        respx_mock.get(f"{base_url}/test").mock(
            return_value=httpx.Response(429, json={"error": "Rate limited"})
        )
        
        client = CallWhiz(api_key="cw_test_123", sandbox=True)
        
        with pytest.raises(RateLimitError, match="Rate limit exceeded"):
            client._request("GET", "/test")

    def test_500_server_error(self, respx_mock, base_url):
        """Test 500 Server Error handling"""
        respx_mock.get(f"{base_url}/test").mock(
            return_value=httpx.Response(500, json={"error": "Server error"})
        )
        
        client = CallWhiz(api_key="cw_test_123", sandbox=True)
        
        with pytest.raises(CallWhizError, match="HTTP 500"):
            client._request("GET", "/test")

    def test_api_error_response(self, respx_mock, base_url):
        """Test API error response format"""
        respx_mock.get(f"{base_url}/test").mock(
            return_value=httpx.Response(200, json={
                "success": False,
                "error": {
                    "code": "CUSTOM_ERROR",
                    "message": "Custom error message"
                }
            })
        )
        
        client = CallWhiz(api_key="cw_test_123", sandbox=True)
        
        with pytest.raises(CallWhizError, match="Custom error message"):
            client._request("GET", "/test")

    def test_network_error(self, respx_mock, base_url):
        """Test network connection error"""
        respx_mock.get(f"{base_url}/test").mock(
            side_effect=httpx.ConnectError("Connection failed")
        )
        
        client = CallWhiz(api_key="cw_test_123", sandbox=True)
        
        with pytest.raises(CallWhizError, match="Request failed"):
            client._request("GET", "/test")


class TestAgentMethods:
    """Test agent-related client methods"""

    def test_create_agent(self, respx_mock, base_url, sample_agent_data, mock_success_response):
        """Test creating an agent"""
        respx_mock.post(f"{base_url}/agents").mock(
            return_value=httpx.Response(200, json=mock_success_response(sample_agent_data))
        )
        
        client = CallWhiz(api_key="cw_test_123", sandbox=True)
        
        agent = client.create_agent(
            name="Test Agent",
            voice={"provider": "openai", "voice_id": "alloy"},
            llm={"provider": "openai", "model": "gpt-4"},
            prompt="You are helpful"
        )
        
        assert isinstance(agent, Agent)
        assert agent.name == "Test Agent"
        assert agent.id == "agent_123"

    def test_create_agent_with_all_fields(self, respx_mock, base_url, sample_agent_data, mock_success_response):
        """Test creating agent with all optional fields"""
        respx_mock.post(f"{base_url}/agents").mock(
            return_value=httpx.Response(200, json=mock_success_response(sample_agent_data))
        )
        
        client = CallWhiz(api_key="cw_test_123", sandbox=True)
        
        agent = client.create_agent(
            name="Complete Agent",
            voice={"provider": "elevenlabs", "voice_id": "voice_123", "speed": 1.2, "pitch": 0.8},
            llm={"provider": "anthropic", "model": "claude-3", "temperature": 0.5, "max_tokens": 200},
            prompt="You are a complete agent",
            description="Complete agent description",
            first_message="Hello there!",
            settings={
                "max_call_duration": 900,
                "enable_interruptions": False,
                "silence_timeout": 10,
                "response_delay": 1.0
            }
        )
        
        assert isinstance(agent, Agent)
        
        # Verify the request was made with correct data
        request = respx_mock.calls[-1].request
        request_data = request.read().decode()
        assert "Complete Agent" in request_data
        assert "elevenlabs" in request_data
        assert "claude-3" in request_data

    def test_get_agent(self, respx_mock, base_url, sample_agent_data, mock_success_response):
        """Test getting an agent by ID"""
        respx_mock.get(f"{base_url}/agents/agent_123").mock(
            return_value=httpx.Response(200, json=mock_success_response(sample_agent_data))
        )
        
        client = CallWhiz(api_key="cw_test_123", sandbox=True)
        agent = client.get_agent("agent_123")
        
        assert isinstance(agent, Agent)
        assert agent.id == "agent_123"

    def test_list_agents(self, respx_mock, base_url, sample_agent_data, mock_success_response):
        """Test listing agents"""
        respx_mock.get(f"{base_url}/agents").mock(
            return_value=httpx.Response(200, json=mock_success_response([sample_agent_data]))
        )
        
        client = CallWhiz(api_key="cw_test_123", sandbox=True)
        agents = client.list_agents()
        
        assert isinstance(agents, list)
        assert len(agents) == 1
        assert isinstance(agents[0], Agent)

    def test_list_agents_with_filters(self, respx_mock, base_url, sample_agent_data, mock_success_response):
        """Test listing agents with filters"""
        respx_mock.get(f"{base_url}/agents").mock(
            return_value=httpx.Response(200, json=mock_success_response([sample_agent_data]))
        )
        
        client = CallWhiz(api_key="cw_test_123", sandbox=True)
        agents = client.list_agents(page=2, limit=10, status="active")
        
        # Check that query parameters were sent
        request = respx_mock.calls[-1].request
        assert "page=2" in str(request.url)
        assert "limit=10" in str(request.url)
        assert "status=active" in str(request.url)

    def test_update_agent(self, respx_mock, base_url, sample_agent_data, mock_success_response):
        """Test updating an agent"""
        updated_data = sample_agent_data.copy()
        updated_data["name"] = "Updated Agent"
        
        respx_mock.put(f"{base_url}/agents/agent_123").mock(
            return_value=httpx.Response(200, json=mock_success_response(updated_data))
        )
        
        client = CallWhiz(api_key="cw_test_123", sandbox=True)
        agent = client.update_agent(
            agent_id="agent_123",
            name="Updated Agent",
            status="inactive"
        )
        
        assert isinstance(agent, Agent)

    def test_delete_agent(self, respx_mock, base_url, mock_success_response):
        """Test deleting an agent"""
        respx_mock.delete(f"{base_url}/agents/agent_123").mock(
            return_value=httpx.Response(200, json=mock_success_response({"message": "Deleted"}))
        )
        
        client = CallWhiz(api_key="cw_test_123", sandbox=True)
        result = client.delete_agent("agent_123")
        
        assert result is True


class TestCallMethods:
    """Test call-related client methods"""

    def test_start_call(self, respx_mock, base_url, sample_call_data, mock_success_response):
        """Test starting a call"""
        respx_mock.post(f"{base_url}/calls").mock(
            return_value=httpx.Response(200, json=mock_success_response(sample_call_data))
        )
        
        client = CallWhiz(api_key="cw_test_123", sandbox=True)
        call = client.start_call(
            agent_id="agent_123",
            phone_number="+1234567890"
        )
        
        assert isinstance(call, Call)
        assert call.call_id == "call_123"
        assert call.agent_id == "agent_123"

    def test_start_call_with_context(self, respx_mock, base_url, sample_call_data, mock_success_response):
        """Test starting call with context and metadata"""
        respx_mock.post(f"{base_url}/calls").mock(
            return_value=httpx.Response(200, json=mock_success_response(sample_call_data))
        )
        
        client = CallWhiz(api_key="cw_test_123", sandbox=True)
        call = client.start_call(
            agent_id="agent_123",
            phone_number="+1234567890",
            context={"customer_name": "John Doe", "account_id": "acc_123"},
            webhook_url="https://example.com/webhook",
            metadata={"campaign": "summer2024"}
        )
        
        assert isinstance(call, Call)
        
        # Verify request data
        request = respx_mock.calls[-1].request
        request_data = request.read().decode()
        assert "John Doe" in request_data
        assert "webhook" in request_data

    def test_get_call(self, respx_mock, base_url, sample_call_data, mock_success_response):
        """Test getting call status"""
        respx_mock.get(f"{base_url}/calls/call_123").mock(
            return_value=httpx.Response(200, json=mock_success_response(sample_call_data))
        )
        
        client = CallWhiz(api_key="cw_test_123", sandbox=True)
        call = client.get_call("call_123")
        
        assert isinstance(call, Call)
        assert call.call_id == "call_123"

    def test_list_calls(self, respx_mock, base_url, sample_call_data, mock_success_response):
        """Test listing calls"""
        respx_mock.get(f"{base_url}/calls").mock(
            return_value=httpx.Response(200, json=mock_success_response([sample_call_data]))
        )
        
        client = CallWhiz(api_key="cw_test_123", sandbox=True)
        calls = client.list_calls()
        
        assert isinstance(calls, list)
        assert len(calls) == 1
        assert isinstance(calls[0], Call)

    def test_list_calls_with_filters(self, respx_mock, base_url, sample_call_data, mock_success_response):
        """Test listing calls with filters"""
        respx_mock.get(f"{base_url}/calls").mock(
            return_value=httpx.Response(200, json=mock_success_response([sample_call_data]))
        )
        
        client = CallWhiz(api_key="cw_test_123", sandbox=True)
        calls = client.list_calls(
            agent_id="agent_123",
            status="completed",
            from_date="2024-01-01",
            to_date="2024-12-31"
        )
        
        # Check query parameters
        request = respx_mock.calls[-1].request
        url_str = str(request.url)
        assert "agent_id=agent_123" in url_str
        assert "status=completed" in url_str
        assert "from_date=2024-01-01" in url_str

    def test_get_call_transcript(self, respx_mock, base_url, mock_success_response):
        """Test getting call transcript"""
        transcript_data = {
            "call_id": "call_123",
            "transcript": [
                {"timestamp": "2024-01-01T10:00:00Z", "speaker": "agent", "text": "Hello!"},
                {"timestamp": "2024-01-01T10:00:05Z", "speaker": "customer", "text": "Hi there!"}
            ],
            "duration": 120,
            "word_count": 4
        }
        
        respx_mock.get(f"{base_url}/calls/call_123/transcript").mock(
            return_value=httpx.Response(200, json=mock_success_response(transcript_data))
        )
        
        client = CallWhiz(api_key="cw_test_123", sandbox=True)
        transcript = client.get_call_transcript("call_123")
        
        assert transcript["call_id"] == "call_123"
        assert len(transcript["transcript"]) == 2

    def test_get_call_recording(self, respx_mock, base_url, mock_success_response):
        """Test getting call recording"""
        recording_data = {
            "call_id": "call_123",
            "recording_url": "https://example.com/recording.mp3",
            "duration": 120,
            "format": "mp3",
            "size_bytes": 1024000,
            "expires_at": "2024-01-02T10:00:00Z"
        }
        
        respx_mock.get(f"{base_url}/calls/call_123/recording").mock(
            return_value=httpx.Response(200, json=mock_success_response(recording_data))
        )
        
        client = CallWhiz(api_key="cw_test_123", sandbox=True)
        recording = client.get_call_recording("call_123")
        
        assert recording["call_id"] == "call_123"
        assert recording["format"] == "mp3"


class TestWebhookMethods:
    """Test webhook-related client methods"""

    def test_create_webhook(self, respx_mock, base_url, sample_webhook_data, mock_success_response):
        """Test creating a webhook"""
        respx_mock.post(f"{base_url}/webhooks").mock(
            return_value=httpx.Response(200, json=mock_success_response(sample_webhook_data))
        )
        
        client = CallWhiz(api_key="cw_test_123", sandbox=True)
        webhook = client.create_webhook(
            url="https://example.com/webhook",
            events=["call.started", "call.completed"]
        )
        
        assert isinstance(webhook, Webhook)
        assert webhook.webhook_id == "webhook_123"

    def test_create_webhook_with_options(self, respx_mock, base_url, sample_webhook_data, mock_success_response):
        """Test creating webhook with all options"""
        respx_mock.post(f"{base_url}/webhooks").mock(
            return_value=httpx.Response(200, json=mock_success_response(sample_webhook_data))
        )
        
        client = CallWhiz(api_key="cw_test_123", sandbox=True)
        webhook = client.create_webhook(
            url="https://example.com/webhook",
            events=["call.started"],
            agent_ids=["agent_123"],
            retry_policy={"max_retries": 5, "retry_delay": 120},
            headers={"Authorization": "Bearer token"}
        )
        
        assert isinstance(webhook, Webhook)

    def test_list_webhooks(self, respx_mock, base_url, sample_webhook_data, mock_success_response):
        """Test listing webhooks"""
        respx_mock.get(f"{base_url}/webhooks").mock(
            return_value=httpx.Response(200, json=mock_success_response([sample_webhook_data]))
        )
        
        client = CallWhiz(api_key="cw_test_123", sandbox=True)
        webhooks = client.list_webhooks()
        
        assert isinstance(webhooks, list)
        assert len(webhooks) == 1
        assert isinstance(webhooks[0], Webhook)

    def test_get_webhook(self, respx_mock, base_url, sample_webhook_data, mock_success_response):
        """Test getting a webhook"""
        respx_mock.get(f"{base_url}/webhooks/webhook_123").mock(
            return_value=httpx.Response(200, json=mock_success_response(sample_webhook_data))
        )
        
        client = CallWhiz(api_key="cw_test_123", sandbox=True)
        webhook = client.get_webhook("webhook_123")
        
        assert isinstance(webhook, Webhook)
        assert webhook.webhook_id == "webhook_123"

    def test_update_webhook(self, respx_mock, base_url, sample_webhook_data, mock_success_response):
        """Test updating a webhook"""
        respx_mock.put(f"{base_url}/webhooks/webhook_123").mock(
            return_value=httpx.Response(200, json=mock_success_response(sample_webhook_data))
        )
        
        client = CallWhiz(api_key="cw_test_123", sandbox=True)
        webhook = client.update_webhook(
            webhook_id="webhook_123",
            active=False,
            events=["call.completed"]
        )
        
        assert isinstance(webhook, Webhook)

    def test_delete_webhook(self, respx_mock, base_url, mock_success_response):
        """Test deleting a webhook"""
        respx_mock.delete(f"{base_url}/webhooks/webhook_123").mock(
            return_value=httpx.Response(200, json=mock_success_response({"message": "Deleted"}))
        )
        
        client = CallWhiz(api_key="cw_test_123", sandbox=True)
        result = client.delete_webhook("webhook_123")
        
        assert result is True

    def test_get_available_webhook_events(self, respx_mock, base_url, mock_success_response):
        """Test getting available webhook events"""
        events = ["call.started", "call.completed", "call.failed", "agent.created"]
        
        respx_mock.get(f"{base_url}/webhooks/events").mock(
            return_value=httpx.Response(200, json=mock_success_response(events))
        )
        
        client = CallWhiz(api_key="cw_test_123", sandbox=True)
        available_events = client.get_available_webhook_events()
        
        assert isinstance(available_events, list)
        assert "call.started" in available_events