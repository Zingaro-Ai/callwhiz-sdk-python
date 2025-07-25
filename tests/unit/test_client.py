# tests/unit/test_client.py - UPDATED FOR v2.0.0
import pytest
import httpx
import respx
from unittest.mock import Mock, patch

from callwhiz import CallWhiz, Agent, Call, UserWebhook, CallStage
from callwhiz.exceptions import CallWhizError, AuthenticationError, NotFoundError, RateLimitError


class TestCallWhizClientV2:
    """Test CallWhiz client v2.0.0 with new authentication and structure"""

    def test_client_initialization_v2(self):
        """Test client initialization with Bearer auth"""
        client = CallWhiz(api_key="cw_test_123", base_url="http://localhost:9000/v1")
        
        assert client.api_key == "cw_test_123"
        assert "9000" in client.base_url
        assert client.session.headers["Authorization"] == "Bearer cw_test_123"
        assert client.session.headers["Content-Type"] == "application/json"

    def test_client_initialization_no_api_key(self):
        """Test client initialization without API key"""
        with pytest.raises(ValueError, match="API key is required"):
            CallWhiz(api_key="")

        with pytest.raises(ValueError, match="API key is required"):
            CallWhiz(api_key=None)

    def test_client_default_base_url(self):
        """Test client with default base URL"""
        client = CallWhiz(api_key="cw_test_123")
        assert "9000" in client.base_url
        assert client.base_url.endswith("/v1")

    @respx.mock
    def test_create_agent_new_structure(self):
        """Test creating agent with new simplified structure"""
        # Mock response
        agent_data = {
            "id": "agent_123",
            "name": "Test Agent v2",
            "model": "nano",
            "voice": "Calvin",
            "language": "en",
            "accent": "American",
            "status": "active",
            "created_at": "2024-01-01T10:00:00Z",
            "updated_at": "2024-01-01T10:00:00Z",
            "webhook_ids": [],
            "has_stages": False,
            "stage_count": 1
        }
        
        respx.post("http://localhost:9000/v1/agents").mock(
            return_value=httpx.Response(200, json={"success": True, "data": agent_data})
        )
        
        client = CallWhiz(api_key="cw_test_123")
        
        agent = client.create_agent(
            name="Test Agent v2",
            model="nano",
            voice="Calvin",
            language="en",
            accent="American",
            prompt="You are helpful"
        )
        
        assert isinstance(agent, Agent)
        assert agent.name == "Test Agent v2"
        assert agent.model == "nano"
        assert agent.voice == "Calvin"
        assert agent.language == "en"
        assert agent.accent == "American"
        assert agent.has_stages is False

    @respx.mock
    def test_create_multi_stage_agent(self):
        """Test creating multi-stage agent"""
        agent_data = {
            "id": "agent_multi_123",
            "name": "Multi-Stage Agent",
            "model": "lite",
            "voice": "Olivia",
            "language": "en",
            "accent": None,
            "status": "active",
            "created_at": "2024-01-01T10:00:00Z",
            "updated_at": "2024-01-01T10:00:00Z",
            "webhook_ids": [],
            "has_stages": True,
            "stage_count": 3
        }
        
        respx.post("http://localhost:9000/v1/agents").mock(
            return_value=httpx.Response(200, json={"success": True, "data": agent_data})
        )
        
        client = CallWhiz(api_key="cw_test_123")
        
        stages = [
            CallStage(name="greeting", prompt="Greet the customer"),
            CallStage(name="assistance", prompt="Help the customer"),
            CallStage(name="closing", prompt="Close the conversation")
        ]
        
        agent = client.create_agent(
            name="Multi-Stage Agent",
            model="lite",
            voice="Olivia",
            language="en",
            stages=stages
        )
        
        assert isinstance(agent, Agent)
        assert agent.has_stages is True
        assert agent.stage_count == 3

    def test_create_agent_validation_v2(self):
        """Test agent creation validation with new structure"""
        client = CallWhiz(api_key="cw_test_123")
        
        # Should raise error if neither prompt nor stages provided
        with pytest.raises(ValueError, match="Either 'prompt' or 'stages' must be provided"):
            client.create_agent(
                name="Invalid Agent",
                model="nano",
                voice="Calvin",
                language="en"
            )
        
        # Should raise error if both prompt and stages provided
        stages = [CallStage(name="test", prompt="test")]
        with pytest.raises(ValueError, match="Provide either 'prompt' for single-stage or 'stages' for multi-stage"):
            client.create_agent(
                name="Invalid Agent",
                model="nano", 
                voice="Calvin",
                language="en",
                prompt="Test prompt",
                stages=stages
            )

    @respx.mock
    def test_create_user_webhook(self):
        """Test creating user webhook (function)"""
        webhook_data = {
            "id": "webhook_123",
            "name": "test_function",
            "description": "Test function",
            "endpoint": "https://api.example.com/test",
            "method": "POST",
            "parameters": {},
            "created_at": "2024-01-01T10:00:00Z",
            "auth_type": "none",
            "has_auth": False
        }
        
        respx.post("http://localhost:9000/v1/user-webhooks").mock(
            return_value=httpx.Response(200, json={"success": True, "data": webhook_data})
        )
        
        client = CallWhiz(api_key="cw_test_123")
        
        webhook = client.create_user_webhook(
            name="test_function",
            description="Test function",
            endpoint="https://api.example.com/test",
            method="POST",
            parameters={
                "message": {
                    "type": "string",
                    "description": "Message to send",
                    "required": True
                }
            }
        )
        
        assert isinstance(webhook, UserWebhook)
        assert webhook.name == "test_function"
        assert webhook.endpoint == "https://api.example.com/test"

    @respx.mock
    def test_get_credits_simple(self):
        """Test getting simple credits information"""
        credits_data = {
            "credits_remaining": 45.5,
            "total_credits": 100,
            "usage_percentage": 54.5
        }
        
        respx.get("http://localhost:9000/v1/credits/simple").mock(
            return_value=httpx.Response(200, json={"success": True, "data": credits_data})
        )
        
        client = CallWhiz(api_key="cw_test_123")
        credits = client.get_credits_simple()
        
        assert credits.credits_remaining == 45.5
        assert credits.total_credits == 100
        assert credits.usage_percentage == 54.5

    @respx.mock
    def test_get_credits_detailed(self):
        """Test getting detailed credits information"""
        credits_data = {
            "user_id": "user_123",
            "email": "test@example.com",
            "credits_remaining": 45.5,
            "monthly_credits": 100,
            "total_credits": 100,
            "plan_id": "professional",
            "billing_active": True,
            "next_renewal_date": "2024-02-01T10:00:00Z",
            "created_at": "2024-01-01T10:00:00Z"
        }
        
        respx.get("http://localhost:9000/v1/credits/balance").mock(
            return_value=httpx.Response(200, json={"success": True, "data": credits_data})
        )
        
        client = CallWhiz(api_key="cw_test_123")
        credits = client.get_credits_detailed()
        
        assert credits.email == "test@example.com"
        assert credits.plan_id == "professional"
        assert credits.billing_active is True

    @respx.mock
    def test_check_credits_by_owner_id(self):
        """Test checking credits using owner ID"""
        owner_id = "owner_123"
        credits_data = {
            "credits_remaining": 30.0,
            "total_credits": 100,
            "usage_percentage": 70.0
        }
        
        respx.get(f"http://localhost:9000/v1/credits/check/{owner_id}").mock(
            return_value=httpx.Response(200, json={"success": True, "data": credits_data})
        )
        
        client = CallWhiz(api_key="cw_test_123")
        credits = client.check_credits_by_owner_id(owner_id)
        
        assert credits.credits_remaining == 30.0
        assert credits.usage_percentage == 70.0

    @respx.mock
    def test_get_user_phone_numbers(self):
        """Test getting user phone numbers"""
        phone_data = [
            {"phone_number": "+15551234567", "max_channels": 2},
            {"phone_number": "+15559876543", "max_channels": 1}
        ]
        
        respx.get("http://localhost:9000/v1/phone-numbers").mock(
            return_value=httpx.Response(200, json={"success": True, "data": phone_data})
        )
        
        client = CallWhiz(api_key="cw_test_123")
        phones = client.get_user_phone_numbers()
        
        assert len(phones) == 2
        assert phones[0].phone_number == "+15551234567"
        assert phones[0].max_channels == 2

    @respx.mock
    def test_error_handling_v2(self):
        """Test error handling with new API responses"""
        # Test 401 with new auth
        respx.get("http://localhost:9000/v1/agents").mock(
            return_value=httpx.Response(401, json={
                "success": False,
                "error": {
                    "code": "UNAUTHORIZED",
                    "message": "Invalid API key"
                }
            })
        )
        
        client = CallWhiz(api_key="invalid_key")
        
        with pytest.raises(AuthenticationError, match="Invalid API key"):
            client.list_agents()

    @respx.mock
    def test_api_error_response_v2(self):
        """Test API error response format v2"""
        respx.get("http://localhost:9000/v1/agents/nonexistent").mock(
            return_value=httpx.Response(200, json={
                "success": False,
                "error": {
                    "code": "NOT_FOUND", 
                    "message": "Agent not found",
                    "details": {"agent_id": "nonexistent"}
                }
            })
        )
        
        client = CallWhiz(api_key="cw_test_123")
        
        with pytest.raises(CallWhizError, match="Agent not found"):
            client.get_agent("nonexistent")

    def test_bearer_auth_header(self):
        """Test that Bearer authentication header is set correctly"""
        client = CallWhiz(api_key="cw_test_mykey123")
        
        assert "Authorization" in client.session.headers
        assert client.session.headers["Authorization"] == "Bearer cw_test_mykey123"
        assert "X-API-Key" not in client.session.headers  # Old header should not be present


class TestCallWhizModelsV2:
    """Test new models in v2.0.0"""
    
    def test_call_stage_model(self):
        """Test CallStage model"""
        stage = CallStage(
            name="greeting",
            prompt="Welcome the customer",
            webhook_ids=["webhook_123"]
        )
        
        assert stage.name == "greeting"
        assert stage.prompt == "Welcome the customer"
        assert stage.webhook_ids == ["webhook_123"]
    
    def test_agent_model_v2(self):
        """Test updated Agent model"""
        agent_data = {
            "id": "agent_123",
            "name": "Test Agent",
            "model": "nano",
            "voice": "Calvin",
            "language": "en",
            "accent": "American",
            "status": "active",
            "created_at": "2024-01-01T10:00:00Z",
            "updated_at": "2024-01-01T10:00:00Z",
            "webhook_ids": ["webhook_123"],
            "has_stages": True,
            "stage_count": 2
        }
        
        agent = Agent(**agent_data)
        
        assert agent.model == "nano"
        assert agent.voice == "Calvin"
        assert agent.language == "en"
        assert agent.accent == "American"
        assert agent.has_stages is True
        assert agent.stage_count == 2
        assert len(agent.webhook_ids) == 1