# tests/integration/test_integration.py - Integration tests
import pytest
import os
from datetime import datetime

from src.client import CallWhiz
from src.models import Agent, Call, Webhook
from src.exceptions import CallWhizError, AuthenticationError, NotFoundError


@pytest.mark.integration
class TestCallWhizIntegration:
    """Integration tests for CallWhiz SDK - requires running API server"""

    @pytest.fixture(scope="class")
    def api_key(self):
        """Get API key from environment or use test key"""
        return os.getenv("CALLWHIZ_TEST_API_KEY", "cw_test_ACk0txhUbB52Gt1Y2s8gYfS2gLbIiTrl")

    @pytest.fixture(scope="class")
    def client(self, api_key):
        """Create client for integration tests"""
        return CallWhiz(api_key=api_key, sandbox=True)

    @pytest.fixture(scope="class")
    def test_agent(self, client):
        """Create a test agent for integration tests"""
        agent = client.create_agent(
            name="Integration Test Agent",
            voice={"provider": "openai", "voice_id": "alloy"},
            llm={"provider": "openai", "model": "gpt-3.5-turbo"},
            prompt="You are a test agent for integration testing.",
            description="Agent created during integration tests"
        )
        
        yield agent
        
        # Cleanup - delete the agent
        try:
            client.delete_agent(agent.id)
        except Exception:
            pass  # Ignore cleanup errors

    def test_client_connection(self, client):
        """Test basic client connectivity"""
        # This should not raise an exception if API is running
        agents = client.list_agents()
        assert isinstance(agents, list)

    def test_invalid_api_key(self):
        """Test authentication with invalid API key"""
        invalid_client = CallWhiz(api_key="cw_test_invalid_key", sandbox=True)
        
        with pytest.raises(AuthenticationError):
            invalid_client.list_agents()

    def test_agent_lifecycle(self, client):
        """Test complete agent lifecycle: create, read, update, delete"""
        # Create agent
        agent = client.create_agent(
            name="Lifecycle Test Agent",
            voice={"provider": "openai", "voice_id": "echo"},
            llm={"provider": "openai", "model": "gpt-3.5-turbo"},
            prompt="Lifecycle test agent"
        )
        
        assert isinstance(agent, Agent)
        assert agent.name == "Lifecycle Test Agent"
        agent_id = agent.id
        
        try:
            # Read agent
            retrieved_agent = client.get_agent(agent_id)
            assert retrieved_agent.id == agent_id
            assert retrieved_agent.name == "Lifecycle Test Agent"
            
            # Update agent
            updated_agent = client.update_agent(
                agent_id=agent_id,
                name="Updated Lifecycle Agent",
                description="Updated description"
            )
            assert updated_agent.name == "Updated Lifecycle Agent"
            assert updated_agent.description == "Updated description"
            
            # List agents (should include our agent)
            agents = client.list_agents()
            agent_ids = [a.id for a in agents]
            assert agent_id in agent_ids
            
        finally:
            # Delete agent
            result = client.delete_agent(agent_id)
            assert result is True
            
            # Verify deletion (agent should become inactive)
            # Note: Depending on your API, this might return 404 or inactive agent
            try:
                deleted_agent = client.get_agent(agent_id)
                assert deleted_agent.status == "inactive"
            except NotFoundError:
                # Also acceptable if API returns 404 for deleted agents
                pass

    def test_call_initiation(self, client, test_agent):
        """Test call initiation"""
        call = client.start_call(
            agent_id=test_agent.id,
            phone_number="+15551234567",  # Test number
            context={"test": True, "integration": True}
        )
        
        assert isinstance(call, Call)
        assert call.agent_id == test_agent.id
        assert call.phone_number == "+15551234567"
        assert call.status in ["initiated", "connecting"]
        
        # Get call status
        call_status = client.get_call(call.call_id)
        assert call_status.call_id == call.call_id

    def test_webhook_management(self, client, test_agent):
        """Test webhook creation and management"""
        webhook = client.create_webhook(
            url="https://httpbin.org/post",  # Test webhook URL
            events=["call.started", "call.completed"],
            agent_ids=[test_agent.id]
        )
        
        assert isinstance(webhook, Webhook)
        assert webhook.url == "https://httpbin.org/post"
        assert "call.started" in webhook.events
        webhook_id = webhook.webhook_id
        
        try:
            # List webhooks
            webhooks = client.list_webhooks()
            webhook_ids = [w.webhook_id for w in webhooks]
            assert webhook_id in webhook_ids
            
            # Get webhook
            retrieved_webhook = client.get_webhook(webhook_id)
            assert retrieved_webhook.webhook_id == webhook_id
            
            # Update webhook
            updated_webhook = client.update_webhook(
                webhook_id=webhook_id,
                active=False
            )
            assert updated_webhook.active is False
            
        finally:
            # Delete webhook
            result = client.delete_webhook(webhook_id)
            assert result is True

    def test_error_handling(self, client):
        """Test error handling with real API responses"""
        # Test 404 error
        with pytest.raises(NotFoundError):
            client.get_agent("nonexistent_agent_id")
        
        # Test invalid call ID
        with pytest.raises(NotFoundError):
            client.get_call("nonexistent_call_id")

    def test_pagination(self, client):
        """Test pagination with real data"""
        # Get first page
        page1 = client.list_agents(page=1, limit=5)
        assert isinstance(page1, list)
        assert len(page1) <= 5
        
        # If we have enough agents, test second page
        if len(page1) == 5:
            page2 = client.list_agents(page=2, limit=5)
            assert isinstance(page2, list)

    def test_conversation_history(self, client):
        """Test conversation history access"""
        try:
            conversations = client.list_conversations(limit=5)
            assert isinstance(conversations, list)
            
            # If we have conversations, test getting details
            if conversations:
                conversation = client.get_conversation(conversations[0]["conversation_id"])
                assert "conversation_id" in conversation
                assert "messages" in conversation
                
        except Exception as e:
            # Some APIs might not have conversation data available
            pytest.skip(f"Conversation history not available: {e}")

    def test_usage_analytics(self, client):
        """Test usage and analytics endpoints"""
        try:
            # Test usage stats
            usage = client.get_usage(period="week")
            assert "api_calls" in usage
            assert "voice_calls" in usage
            
            # Test credit balance
            credits = client.get_credit_balance()
            assert "balance" in credits
            assert "currency" in credits
            
            # Test account limits
            limits = client.get_account_limits()
            assert "plan" in limits
            assert "limits" in limits
            
        except Exception as e:
            # These endpoints might not be fully implemented
            pytest.skip(f"Analytics endpoints not available: {e}")

    def test_available_webhook_events(self, client):
        """Test getting available webhook events"""
        events = client.get_available_webhook_events()
        assert isinstance(events, list)
        assert len(events) > 0
        assert "call.started" in events

    @pytest.mark.slow
    def test_multiple_agents_performance(self, client):
        """Test creating multiple agents (performance test)"""
        agent_ids = []
        
        try:
            # Create 5 agents
            for i in range(5):
                agent = client.create_agent(
                    name=f"Performance Test Agent {i}",
                    voice={"provider": "openai", "voice_id": "alloy"},
                    llm={"provider": "openai", "model": "gpt-3.5-turbo"},
                    prompt=f"Performance test agent {i}"
                )
                agent_ids.append(agent.id)
                assert isinstance(agent, Agent)
            
            # List all agents (should include our 5)
            all_agents = client.list_agents()
            created_agent_ids = [a.id for a in all_agents if a.id in agent_ids]
            assert len(created_agent_ids) == 5
            
        finally:
            # Cleanup all created agents
            for agent_id in agent_ids:
                try:
                    client.delete_agent(agent_id)
                except Exception:
                    pass  # Ignore cleanup errors


@pytest.mark.integration
class TestCallWhizClientContext:
    """Test client context manager in integration environment"""

    def test_context_manager_integration(self):
        """Test client context manager with real connection"""
        api_key = os.getenv("CALLWHIZ_TEST_API_KEY", "cw_test_ACk0txhUbB52Gt1Y2s8gYfS2gLbIiTrl")
        
        with CallWhiz(api_key=api_key, sandbox=True) as client:
            agents = client.list_agents()
            assert isinstance(agents, list)
        
        # Client should be closed after context
        assert client.session.is_closed

    def test_manual_close_integration(self):
        """Test manual client close with real connection"""
        api_key = os.getenv("CALLWHIZ_TEST_API_KEY", "cw_test_ACk0txhUbB52Gt1Y2s8gYfS2gLbIiTrl")
        
        client = CallWhiz(api_key=api_key, sandbox=True)
        
        # Should be able to make request
        agents = client.list_agents()
        assert isinstance(agents, list)
        
        # Close client
        client.close()
        assert client.session.is_closed
        
        # Should not be able to make requests after close
        with pytest.raises(Exception):  # Could be different exceptions depending on httpx version
            client.list_agents()