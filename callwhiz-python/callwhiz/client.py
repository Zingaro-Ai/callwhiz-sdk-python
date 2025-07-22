# callwhiz/client.py - COMPLETE VERSION
import httpx
from typing import List, Optional, Dict, Any, Union
from .models import Agent, Call, Webhook
from .exceptions import CallWhizError, AuthenticationError, NotFoundError, RateLimitError


class CallWhiz:
    def __init__(self, api_key: str, sandbox: bool = True):
        if not api_key:
            raise ValueError("API key is required")
        
        self.api_key = api_key
        self.base_url = "http://localhost:8000/v1/api/developer/v1"  # Local API
        self.session = httpx.Client(
            headers={"X-API-Key": api_key, "Content-Type": "application/json"},
            timeout=30.0
        )
    
    def _request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make HTTP request with error handling"""
        url = f"{self.base_url}{endpoint}"
        
        try:
            response = self.session.request(method, url, **kwargs)
            response.raise_for_status()
            data = response.json()
            
            if not data.get("success"):
                raise CallWhizError(data.get("error", {}).get("message", "Unknown error"))
            
            return data["data"]
            
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                raise AuthenticationError("Invalid API key")
            elif e.response.status_code == 404:
                raise NotFoundError("Resource not found")
            elif e.response.status_code == 429:
                raise RateLimitError("Rate limit exceeded")
            else:
                raise CallWhizError(f"HTTP {e.response.status_code}: {e.response.text}")
        except httpx.RequestError as e:
            raise CallWhizError(f"Request failed: {e}")

    # ===== AGENT METHODS - COMPLETE =====
    def create_agent(
        self,
        name: str,
        voice: Dict[str, Any],
        llm: Dict[str, Any], 
        prompt: str,
        description: Optional[str] = None,
        first_message: Optional[str] = None,
        settings: Optional[Dict[str, Any]] = None
    ) -> Agent:
        """
        Create a new voice agent with all available fields
        
        Args:
            name: Agent name (required)
            voice: Voice configuration (required)
                - provider: "openai", "elevenlabs", etc.
                - voice_id: Voice ID specific to provider
                - speed: 0.5-2.0 (default: 1.0)
                - pitch: 0.5-2.0 (default: 1.0)
            llm: LLM configuration (required)
                - provider: "openai", "anthropic", etc.
                - model: Model name
                - temperature: 0-2 (default: 0.7)
                - max_tokens: 1-4000 (default: 150)
            prompt: System prompt (required)
            description: Agent description (optional)
            first_message: Opening message (optional)
            settings: Agent settings (optional)
                - max_call_duration: 60-7200 seconds (default: 1800)
                - enable_interruptions: bool (default: True)
                - silence_timeout: 1-30 seconds (default: 5)
                - response_delay: 0-5 seconds (default: 0.5)
        """
        data = {
            "name": name,
            "voice": voice,
            "llm": llm,
            "prompt": prompt
        }
        
        if description is not None:
            data["description"] = description
        if first_message is not None:
            data["first_message"] = first_message
        if settings is not None:
            data["settings"] = settings
            
        result = self._request("POST", "/agents", json=data)
        return Agent(**result)
    
    def get_agent(self, agent_id: str) -> Agent:
        """Get agent by ID"""
        result = self._request("GET", f"/agents/{agent_id}")
        return Agent(**result)
    
    def list_agents(
        self, 
        page: int = 1,  
        limit: int = 20, 
        status: Optional[str] = "active"
    ) -> List[Agent]:
        """
        List all agents
        
        Args:
            page: Page number (default: 1)
            limit: Items per page 1-100 (default: 20)
            status: Filter by status - "active", "inactive", "draft"
        """
        params = {"page": page, "limit": limit}
        if status:
            params["status"] = status
            
        result = self._request("GET", "/agents", params=params)
        return [Agent(**agent) for agent in result]
    
    def update_agent(
        self,
        agent_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        voice: Optional[Dict[str, Any]] = None,
        llm: Optional[Dict[str, Any]] = None,
        prompt: Optional[str] = None,
        first_message: Optional[str] = None,
        settings: Optional[Dict[str, Any]] = None,
        status: Optional[str] = None
    ) -> Agent:
        """
        Update agent with any fields
        
        Args:
            agent_id: Agent ID to update
            name: New agent name
            description: New description
            voice: New voice configuration
            llm: New LLM configuration
            prompt: New system prompt
            first_message: New opening message
            settings: New agent settings
            status: New status - "active", "inactive", "draft"
        """
        data = {}
        if name is not None:
            data["name"] = name
        if description is not None:
            data["description"] = description
        if voice is not None:
            data["voice"] = voice
        if llm is not None:
            data["llm"] = llm
        if prompt is not None:
            data["prompt"] = prompt
        if first_message is not None:
            data["first_message"] = first_message
        if settings is not None:
            data["settings"] = settings
        if status is not None:
            data["status"] = status
            
        result = self._request("PUT", f"/agents/{agent_id}", json=data)
        return Agent(**result)
    
    def delete_agent(self, agent_id: str) -> bool:
        """Delete agent (soft delete - becomes inactive)"""
        self._request("DELETE", f"/agents/{agent_id}")
        return True

    # ===== CALL METHODS - COMPLETE =====
    def start_call(
        self,
        agent_id: str,
        phone_number: str,
        context: Optional[Dict[str, Any]] = None,
        webhook_url: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Call:
        """
        Initiate a call with all available fields
        
        Args:
            agent_id: ID of agent to use (required)
            phone_number: Phone number in E.164 format (required)
            context: Additional context for the agent
                - customer_name: Customer name
                - customer_id: Customer ID
                - purpose: Call purpose
                - Any other custom fields
            webhook_url: URL to receive call events
            metadata: Custom metadata for the call
        """
        data = {
            "agent_id": agent_id,
            "phone_number": phone_number
        }
        
        if context is not None:
            data["context"] = context
        if webhook_url is not None:
            data["webhook_url"] = webhook_url
        if metadata is not None:
            data["metadata"] = metadata
            
        result = self._request("POST", "/calls", json=data)
        return Call(**result)
    
    def get_call(self, call_id: str) -> Call:
        """Get call status and details"""
        result = self._request("GET", f"/calls/{call_id}")
        return Call(**result)
    
    def list_calls(
        self, 
        page: int = 1, 
        limit: int = 20,
        agent_id: Optional[str] = None,
        status: Optional[str] = None,
        from_date: Optional[str] = None,
        to_date: Optional[str] = None
    ) -> List[Call]:
        """
        List calls with filters
        
        Args:
            page: Page number
            limit: Items per page
            agent_id: Filter by agent ID
            status: Filter by status - "initiated", "connecting", "active", "completed", "failed"
            from_date: Filter calls after date (ISO 8601)
            to_date: Filter calls before date (ISO 8601)
        """
        params = {"page": page, "limit": limit}
        if agent_id:
            params["agent_id"] = agent_id
        if status:
            params["status"] = status
        if from_date:
            params["from_date"] = from_date
        if to_date:
            params["to_date"] = to_date
            
        result = self._request("GET", "/calls", params=params)
        return [Call(**call) for call in result]

    def get_call_transcript(self, call_id: str) -> Dict[str, Any]:
        """Get call transcript"""
        return self._request("GET", f"/calls/{call_id}/transcript")
    
    def get_call_recording(self, call_id: str) -> Dict[str, Any]:
        """Get call recording URL"""
        return self._request("GET", f"/calls/{call_id}/recording")

    # ===== WEBHOOK METHODS - COMPLETE =====
    def create_webhook(
        self,
        url: str,
        events: List[str],
        agent_ids: Optional[List[str]] = None,
        active: bool = True,
        retry_policy: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> Webhook:
        """
        Create webhook with all available fields
        
        Args:
            url: Webhook URL (required)
            events: List of events to subscribe to (required)
                Available events:
                - "call.started", "call.completed", "call.failed"
                - "call.transcript_ready", "call.recording_ready"
                - "agent.created", "agent.updated", "agent.deleted"
            agent_ids: Filter events for specific agents
            active: Whether webhook is active (default: True)
            retry_policy: Retry configuration
                - max_retries: 0-10 (default: 3)
                - retry_delay: 1-3600 seconds (default: 60)
            headers: Custom headers to send with webhook
        """
        data = {
            "url": url,
            "events": events,
            "active": active
        }
        
        if agent_ids is not None:
            data["agent_ids"] = agent_ids
        if retry_policy is not None:
            data["retry_policy"] = retry_policy
        if headers is not None:
            data["headers"] = headers
            
        result = self._request("POST", "/webhooks", json=data)
        return Webhook(**result)
    
    def list_webhooks(self) -> List[Webhook]:
        """List all webhooks"""
        result = self._request("GET", "/webhooks")
        return [Webhook(**webhook) for webhook in result]
    
    def get_webhook(self, webhook_id: str) -> Webhook:
        """Get webhook by ID"""
        result = self._request("GET", f"/webhooks/{webhook_id}")
        return Webhook(**result)
    
    def update_webhook(
        self,
        webhook_id: str,
        url: Optional[str] = None,
        events: Optional[List[str]] = None,
        agent_ids: Optional[List[str]] = None,
        active: Optional[bool] = None,
        retry_policy: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> Webhook:
        """Update webhook configuration"""
        data = {}
        if url is not None:
            data["url"] = url
        if events is not None:
            data["events"] = events
        if agent_ids is not None:
            data["agent_ids"] = agent_ids
        if active is not None:
            data["active"] = active
        if retry_policy is not None:
            data["retry_policy"] = retry_policy
        if headers is not None:
            data["headers"] = headers
            
        result = self._request("PUT", f"/webhooks/{webhook_id}", json=data)
        return Webhook(**result)
    
    def delete_webhook(self, webhook_id: str) -> bool:
        """Delete webhook"""
        self._request("DELETE", f"/webhooks/{webhook_id}")
        return True

    def get_available_webhook_events(self) -> List[str]:
        """Get list of all available webhook events"""
        result = self._request("GET", "/webhooks/events")
        return result

    # ===== CONVERSATION METHODS =====
    def list_conversations(
        self,
        agent_id: Optional[str] = None,
        page: int = 1,
        limit: int = 20,
        from_date: Optional[str] = None,
        to_date: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """List conversation history"""
        params = {"page": page, "limit": limit}
        if agent_id:
            params["agent_id"] = agent_id
        if from_date:
            params["from_date"] = from_date
        if to_date:
            params["to_date"] = to_date
            
        result = self._request("GET", "/conversations", params=params)
        return result
    
    def get_conversation(self, conversation_id: str) -> Dict[str, Any]:
        """Get detailed conversation data"""
        return self._request("GET", f"/conversations/{conversation_id}")

    # ===== USAGE & ANALYTICS =====
    def get_usage(
        self,
        period: str = "month",
        from_date: Optional[str] = None,
        to_date: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get API usage statistics
        
        Args:
            period: "day", "week", "month"
            from_date: Custom start date (ISO 8601)
            to_date: Custom end date (ISO 8601)
        """
        params = {"period": period}
        if from_date:
            params["from_date"] = from_date
        if to_date:
            params["to_date"] = to_date
            
        return self._request("GET", "/usage", params=params)
    
    def get_credit_balance(self) -> Dict[str, Any]:
        """Get current credit balance"""
        return self._request("GET", "/usage/credits")
    
    def get_account_limits(self) -> Dict[str, Any]:
        """Get account limits and quotas"""
        return self._request("GET", "/usage/limits")

    def close(self):
        """Close the HTTP session"""
        self.session.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()