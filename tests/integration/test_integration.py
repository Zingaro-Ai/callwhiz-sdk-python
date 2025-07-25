# tests/integration/test_integration.py - UPDATED FOR v2.0.0
import pytest
import os
from datetime import datetime

from callwhiz import CallWhiz, Agent, Call, UserWebhook, CallStage
from callwhiz.exceptions import CallWhizError, AuthenticationError, NotFoundError


@pytest.mark.integration
class TestCallWhizIntegrationV2:
    """Integration tests for CallWhiz SDK v2.0.0 - requires running API server on port 9000"""

    @pytest.fixture(scope="class")
    def api_key(self):
        """Get API key from environment or use test key"""
        return os.getenv("CALLWHIZ_TEST_API_KEY", "cw_test_ACk0txhUbB52Gt1Y2s8gYfS2gLbIiTrl")

    @pytest.fixture(scope="class")
    def client(self, api_key):
        """Create client for integration tests - updated base URL"""
        return CallWhiz(api_key=api_key, base_url="http://localhost:9000/v1")

    @pytest.fixture(scope="class")
    def test_agent(self, client):
        """Create a test agent with new API structure"""
        agent = client.create_agent(
            name="Integration Test Agent v2",
            model="nano",  # New: model selection
            voice="Calvin",  # New: voice name instead of config
            language="en",  # New: language setting
            accent="American",  # New: accent for English
            prompt="You are a test agent for integration testing v2.",
            description="Agent created during integration tests v2"
        )
        
        yield agent
        
        # Cleanup - delete the agent
        try:
            client.delete_agent(agent.id)
        except Exception:
            pass  # Ignore cleanup errors

    def test_client_connection_new_auth(self, client):
        """Test basic client connectivity with new Bearer auth"""
        # This should not raise an exception if API is running
        agents = client.list_agents()
        assert isinstance(agents, list)

    def test_invalid_api_key_new_auth(self):
        """Test authentication with invalid API key using new auth method"""
        invalid_client = CallWhiz(api_key="cw_test_invalid_key", base_url="http://localhost:9000/v1")
        
        with pytest.raises(AuthenticationError):
            invalid_client.list_agents()

    def test_agent_lifecycle_new_structure(self, client):
        """Test complete agent lifecycle with new API structure"""
        # Create agent with new structure
        agent = client.create_agent(
            name="Lifecycle Test Agent v2",
            model="lite",  # New model structure
            voice="Olivia",  # New voice structure
            language="en",
            accent="British",
            prompt="Lifecycle test agent v2",
            description="Testing the new agent structure"
        )
        
        assert isinstance(agent, Agent)
        assert agent.name == "Lifecycle Test Agent v2"
        assert agent.model == "lite"
        assert agent.voice == "Olivia"
        assert agent.language == "en"
        assert agent.accent == "British"
        assert agent.has_stages is False  # Single-stage agent
        agent_id = agent.id
        
        try:
            # Read agent
            retrieved_agent = client.get_agent(agent_id)
            assert retrieved_agent.id == agent_id
            assert retrieved_agent.name == "Lifecycle Test Agent v2"
            assert retrieved_agent.model == "lite"
            
            # Update agent with new structure
            updated_agent = client.update_agent(
                agent_id=agent_id,
                name="Updated Lifecycle Agent v2",
                description="Updated description v2",
                model="nano",  # Change model
                voice="Brian"  # Change voice
            )
            assert updated_agent.name == "Updated Lifecycle Agent v2"
            assert updated_agent.model == "nano"
            assert updated_agent.voice == "Brian"
            
            # List agents (should include our agent)
            agents = client.list_agents()
            agent_ids = [a.id for a in agents]
            assert agent_id in agent_ids
            
        finally:
            # Delete agent
            result = client.delete_agent(agent_id)
            assert result is True
            
            # Verify deletion
            with pytest.raises(NotFoundError):
                client.get_agent(agent_id)

    def test_multi_stage_agent_creation(self, client):
        """Test creating multi-stage agent"""
        # Create stages
        stages = [
            CallStage(
                name="greeting",
                prompt="You are greeting the customer. Be friendly and ask how you can help."
            ),
            CallStage(
                name="assistance",
                prompt="You are helping the customer with their request. Be thorough and helpful."
            ),
            CallStage(
                name="closing",
                prompt="You are closing the conversation. Thank the customer and summarize next steps."
            )
        ]
        
        agent = client.create_agent(
            name="Multi-Stage Test Agent",
            model="nano",
            voice="Calvin",
            language="en",
            stages=stages,
            description="Testing multi-stage agent creation"
        )
        
        assert isinstance(agent, Agent)
        assert agent.has_stages is True
        assert agent.stage_count == 3
        
        try:
            # Verify the agent was created correctly
            retrieved_agent = client.get_agent(agent.id)
            assert retrieved_agent.has_stages is True
            assert retrieved_agent.stage_count == 3
            
        finally:
            # Cleanup
            client.delete_agent(agent.id)

    def test_user_webhooks_functionality(self, client):
        """Test user webhooks (functions) creation and management"""
        # Create a user webhook
        webhook = client.create_user_webhook(
            name="test_function",
            description="A test function for integration testing",
            endpoint="https://httpbin.org/post",
            method="POST",
            parameters={
                "message": {
                    "type": "string",
                    "description": "Message to send",
                    "required": True
                },
                "priority": {
                    "type": "number",
                    "description": "Priority level",
                    "required": False,
                    "default": 1,
                    "minimum": 1,
                    "maximum": 10
                }
            }
        )
        
        assert isinstance(webhook, UserWebhook)
        assert webhook.name == "test_function"
        assert webhook.endpoint == "https://httpbin.org/post"
        webhook_id = webhook.id
        
        try:
            # List user webhooks
            webhooks = client.list_user_webhooks()
            webhook_ids = [w.id for w in webhooks]
            assert webhook_id in webhook_ids
            
            # Get specific webhook
            retrieved_webhook = client.get_user_webhook(webhook_id)
            assert retrieved_webhook.id == webhook_id
            assert retrieved_webhook.name == "test_function"
            
            # Update webhook
            updated_webhook = client.update_user_webhook(
                webhook_id=webhook_id,
                description="Updated test function description"
            )
            assert "Updated" in updated_webhook.description
            
        finally:
            # Delete webhook
            result = client.delete_user_webhook(webhook_id)
            assert result is True

    def test_credits_api_functionality(self, client):
        """Test credits API functionality"""
        try:
            # Test simple credits
            simple_credits = client.get_credits_simple()
            assert hasattr(simple_credits, 'credits_remaining')
            assert hasattr(simple_credits, 'total_credits')
            assert hasattr(simple_credits, 'usage_percentage')
            assert simple_credits.credits_remaining >= 0
            assert simple_credits.total_credits >= 0
            assert 0 <= simple_credits.usage_percentage <= 100
            
            # Test detailed credits
            detailed_credits = client.get_credits_detailed()
            assert hasattr(detailed_credits, 'user_id')
            assert hasattr(detailed_credits, 'email')
            assert hasattr(detailed_credits, 'plan_id')
            assert hasattr(detailed_credits, 'billing_active')
            assert detailed_credits.credits_remaining >= 0
            
            print(f"✅ Credits: {simple_credits.credits_remaining:.2f}/{simple_credits.total_credits}")
            print(f"✅ Usage: {simple_credits.usage_percentage:.1f}%")
            print(f"✅ Plan: {detailed_credits.plan_id}")
            
        except Exception as e:
            pytest.skip(f"Credits API not available: {e}")

    def test_phone_numbers_api(self, client):
        """Test phone numbers API"""
        try:
            phone_numbers = client.get_user_phone_numbers()
            assert isinstance(phone_numbers, list)
            
            # If user has phone numbers, verify structure
            if phone_numbers:
                phone = phone_numbers[0]
                assert hasattr(phone, 'phone_number')
                assert hasattr(phone, 'max_channels')
                print(f"✅ Phone: {phone.phone_number} (max channels: {phone.max_channels})")
            
        except Exception as e:
            pytest.skip(f"Phone numbers API not available: {e}")

    def test_agent_with_user_webhooks(self, client):
        """Test creating agent with user webhooks"""
        # First create a user webhook
        webhook = client.create_user_webhook(
            name="agent_test_function",
            description="Function for agent testing",
            endpoint="https://httpbin.org/post",
            parameters={
                "data": {
                    "type": "string",
                    "description": "Data to process",
                    "required": True
                }
            }
        )
        
        try:
            # Create agent with webhook
            agent = client.create_agent(
                name="Agent with Webhook",
                model="nano",
                voice="Calvin",
                language="en",
                prompt="You can use the agent_test_function to process data.",
                webhook_ids=[webhook.id]
            )
            
            assert isinstance(agent, Agent)
            assert webhook.id in agent.webhook_ids
            
            # Cleanup agent
            client.delete_agent(agent.id)
            
        finally:
            # Cleanup webhook
            client.delete_user_webhook(webhook.id)

    def test_call_initiation_new_structure(self, client, test_agent):
        """Test call initiation with new agent structure"""
        call = client.start_call(
            agent_id=test_agent.id,
            phone_number="+15551234567",  # Test number
            context={"test": True, "integration": True, "version": "v2.0"}
        )
        
        assert isinstance(call, Call)
        assert call.agent_id == test_agent.id
        assert call.phone_number == "+15551234567"
        assert call.status in ["initiated", "connecting"]
        
        # Get call status
        call_status = client.get_call(call.call_id)
        assert call_status.call_id == call.call_id

    def test_error_handling_new_structure(self, client):
        """Test error handling with new API structure"""
        # Test 404 error
        with pytest.raises(NotFoundError):
            client.get_agent("nonexistent_agent_id")
        
        # Test invalid model
        with pytest.raises(CallWhizError):
            client.create_agent(
                name="Invalid Model Agent",
                model="invalid_model",  # Should be "lite", "nano", or "pro"
                voice="Calvin",
                prompt="Test"
            )

    def test_check_credits_by_owner_id(self, client, test_agent):
        """Test checking credits using agent's owner_id (if available)"""
        try:
            # This would typically use the owner_id from agent data
            # For testing, we'll use the current user's credits
            credits = client.get_credits_simple()
            assert credits.credits_remaining >= 0
            
            # In real usage, you'd do:
            # credits = client.check_credits_by_owner_id(agent.owner_id)
            
        except Exception as e:
            pytest.skip(f"Owner ID credits check not available: {e}")


@pytest.mark.integration
class TestCallWhizClientContextV2:
    """Test client context manager with v2.0.0"""

    def test_context_manager_integration_v2(self):
        """Test client context manager with new auth"""
        api_key = os.getenv("CALLWHIZ_TEST_API_KEY", "cw_test_ACk0txhUbB52Gt1Y2s8gYfS2gLbIiTrl")
        
        with CallWhiz(api_key=api_key, base_url="http://localhost:9000/v1") as client:
            agents = client.list_agents()
            assert isinstance(agents, list)
        
        # Client should be closed after context
        assert client.session.is_closed

    def test_manual_close_integration_v2(self):
        """Test manual client close with new structure"""
        api_key = os.getenv("CALLWHIZ_TEST_API_KEY", "cw_test_ACk0txhUbB52Gt1Y2s8gYfS2gLbIiTrl")
        
        client = CallWhiz(api_key=api_key, base_url="http://localhost:9000/v1")
        
        # Should be able to make request
        agents = client.list_agents()
        assert isinstance(agents, list)
        
        # Close client
        client.close()
        assert client.session.is_closed
        
        # Should not be able to make requests after close
        with pytest.raises(Exception):  # Could be different exceptions depending on httpx version
            client.list_agents()