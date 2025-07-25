# callwhiz/client.py - UPDATED FOR v2.0.0
import httpx
from typing import List, Optional, Dict, Any, Union
from .models import (
    Agent, Call, Webhook, UserWebhook, 
    UserCreditsResponse, UserCreditsSimpleResponse,
    TranscriptResponse, RecordingResponse,
    CallStage, PhoneNumber
)
from .exceptions import CallWhizError, AuthenticationError, NotFoundError, RateLimitError


class CallWhiz:
    def __init__(self, api_key: str, base_url: str = "http://localhost:9000/v1"):
        if not api_key:
            raise ValueError("API key is required")
        
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        
        # Updated authentication to use Bearer token
        self.session = httpx.Client(
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
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
                error_info = data.get("error", {})
                raise CallWhizError(error_info.get("message", "Unknown error"))
            
            return data["data"]
            
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                raise AuthenticationError("Invalid API key")
            elif e.response.status_code == 404:
                raise NotFoundError("Resource not found")
            elif e.response.status_code == 429:
                raise RateLimitError("Rate limit exceeded")
            else:
                try:
                    error_data = e.response.json()
                    error_msg = error_data.get("error", {}).get("message", f"HTTP {e.response.status_code}")
                except:
                    error_msg = f"HTTP {e.response.status_code}: {e.response.text}"
                raise CallWhizError(error_msg)
        except httpx.RequestError as e:
            raise CallWhizError(f"Request failed: {e}")

    # ===== AGENT METHODS - UPDATED FOR NEW API =====
    def create_agent(
        self,
        name: str,
        model: str,  # "lite", "nano", "pro"
        voice: str,  # Voice name like "Calvin", "Olivia", "Brian"
        prompt: Optional[str] = None,
        stages: Optional[List[CallStage]] = None,
        description: Optional[str] = None,
        language: Optional[str] = None,  # "en", "es", "hi", "te"
        accent: Optional[str] = None,  # "American", "British" (for English only)
        first_message: Optional[str] = None,
        webhook_ids: Optional[List[str]] = None
    ) -> Agent:
        """
        Create a new voice agent with updated API structure
        
        Args:
            name: Agent name (required)
            model: Model type - "lite", "nano", "pro" (required)
            voice: Voice name like "Calvin", "Olivia", "Brian" (required)
            prompt: System prompt for single-stage agent
            stages: List of stages for multi-stage agent
            description: Agent description
            language: Language code - "en", "es", "hi", "te"
            accent: Accent for English voices - "American", "British"
            first_message: Opening message
            webhook_ids: IDs of webhooks agent can use
        
        Note: Provide either 'prompt' for single-stage or 'stages' for multi-stage agent
        """
        if not prompt and not stages:
            raise ValueError("Either 'prompt' or 'stages' must be provided")
        if prompt and stages:
            raise ValueError("Provide either 'prompt' for single-stage or 'stages' for multi-stage, not both")
        
        data = {
            "name": name,
            "model": model,
            "voice": voice
        }
        
        if description is not None:
            data["description"] = description
        if language is not None:
            data["language"] = language
        if accent is not None:
            data["accent"] = accent
        if first_message is not None:
            data["first_message"] = first_message
        if webhook_ids is not None:
            data["webhook_ids"] = webhook_ids
        
        # Single-stage or multi-stage
        if prompt:
            data["prompt"] = prompt
        if stages:
            data["stages"] = [stage.model_dump() for stage in stages]
            
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
        status: Optional[str] = None
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
        model: Optional[str] = None,
        voice: Optional[str] = None,
        language: Optional[str] = None,
        accent: Optional[str] = None,
        prompt: Optional[str] = None,
        first_message: Optional[str] = None,
        webhook_ids: Optional[List[str]] = None,
        stages: Optional[List[CallStage]] = None,
        status: Optional[str] = None
    ) -> Agent:
        """Update agent with new API structure"""
        data = {}
        if name is not None:
            data["name"] = name
        if description is not None:
            data["description"] = description
        if model is not None:
            data["model"] = model
        if voice is not None:
            data["voice"] = voice
        if language is not None:
            data["language"] = language
        if accent is not None:
            data["accent"] = accent
        if prompt is not None:
            data["prompt"] = prompt
        if first_message is not None:
            data["first_message"] = first_message
        if webhook_ids is not None:
            data["webhook_ids"] = webhook_ids
        if stages is not None:
            data["stages"] = [stage.model_dump() for stage in stages]
        if status is not None:
            data["status"] = status
            
        result = self._request("PUT", f"/agents/{agent_id}", json=data)
        return Agent(**result)
    
    def delete_agent(self, agent_id: str) -> bool:
        """Delete agent permanently"""
        self._request("DELETE", f"/agents/{agent_id}")
        return True

    # ===== CALL METHODS - UPDATED =====
    def start_call(
        self,
        agent_id: str,
        phone_number: str,
        context: Optional[Dict[str, Any]] = None,
        webhook_url: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Call:
        """
        Initiate a call (same as before, but updated response handling)
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
        """List calls with filters"""
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

    def get_call_transcript(self, call_id: str) -> TranscriptResponse:
        """Get call transcript"""
        result = self._request("GET", f"/calls/{call_id}/transcript")
        return TranscriptResponse(**result)
    
    def get_call_recording(self, call_id: str) -> RecordingResponse:
        """Get call recording URL"""
        result = self._request("GET", f"/calls/{call_id}/recording")
        return RecordingResponse(**result)

    # ===== WEBHOOK METHODS - SAME AS BEFORE =====
    def create_webhook(
        self,
        url: str,
        events: List[str],
        agent_ids: Optional[List[str]] = None,
        active: bool = True,
        retry_policy: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> Webhook:
        """Create webhook (same as before)"""
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

    # ===== NEW: USER WEBHOOKS (FUNCTIONS) =====
    def create_user_webhook(
        self,
        name: str,
        description: str,
        endpoint: str,
        method: str = "POST",
        parameters: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        auth_type: Optional[str] = None,
        auth_header_name: Optional[str] = None,
        auth_value: Optional[str] = None
    ) -> UserWebhook:
        """
        Create a user webhook (function) that agents can call
        
        Args:
            name: Function name (alphanumeric + underscore only)
            description: What this function does
            endpoint: URL to call
            method: HTTP method (default: POST)
            parameters: Function parameters with JSON Schema
            headers: Custom headers to send
            auth_type: "none", "api_key", "bearer"
            auth_header_name: Header name for auth
            auth_value: Auth token/key
        """
        data = {
            "name": name,
            "description": description,
            "endpoint": endpoint,
            "method": method
        }
        
        if parameters is not None:
            data["parameters"] = parameters
        if headers is not None:
            data["headers"] = headers
        if auth_type is not None:
            data["auth_type"] = auth_type
        if auth_header_name is not None:
            data["auth_header_name"] = auth_header_name
        if auth_value is not None:
            data["auth_value"] = auth_value
            
        result = self._request("POST", "/user-webhooks", json=data)
        return UserWebhook(**result)
    
    def list_user_webhooks(self) -> List[UserWebhook]:
        """List all user webhooks (functions)"""
        result = self._request("GET", "/user-webhooks")
        return [UserWebhook(**webhook) for webhook in result]
    
    def get_user_webhook(self, webhook_id: str) -> UserWebhook:
        """Get user webhook by ID"""
        result = self._request("GET", f"/user-webhooks/{webhook_id}")
        return UserWebhook(**result)
    
    def update_user_webhook(
        self,
        webhook_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        endpoint: Optional[str] = None,
        method: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        auth_type: Optional[str] = None,
        auth_header_name: Optional[str] = None,
        auth_value: Optional[str] = None
    ) -> UserWebhook:
        """Update user webhook"""
        data = {}
        if name is not None:
            data["name"] = name
        if description is not None:
            data["description"] = description
        if endpoint is not None:
            data["endpoint"] = endpoint
        if method is not None:
            data["method"] = method
        if parameters is not None:
            data["parameters"] = parameters
        if headers is not None:
            data["headers"] = headers
        if auth_type is not None:
            data["auth_type"] = auth_type
        if auth_header_name is not None:
            data["auth_header_name"] = auth_header_name
        if auth_value is not None:
            data["auth_value"] = auth_value
            
        result = self._request("PUT", f"/user-webhooks/{webhook_id}", json=data)
        return UserWebhook(**result)
    
    def delete_user_webhook(self, webhook_id: str) -> bool:
        """Delete user webhook"""
        self._request("DELETE", f"/user-webhooks/{webhook_id}")
        return True

    # ===== NEW: CREDITS API =====
    def get_credits_simple(self, user_id: Optional[str] = None) -> UserCreditsSimpleResponse:
        """
        Get simple credits information
        
        Args:
            user_id: User ID (optional, uses current user if not provided)
        """
        params = {}
        if user_id:
            params["user_id"] = user_id
            
        result = self._request("GET", "/credits/simple", params=params)
        return UserCreditsSimpleResponse(**result)
    
    def get_credits_detailed(self, user_id: Optional[str] = None) -> UserCreditsResponse:
        """
        Get detailed credits information including billing details
        
        Args:
            user_id: User ID (optional, uses current user if not provided)
        """
        params = {}
        if user_id:
            params["user_id"] = user_id
            
        result = self._request("GET", "/credits/balance", params=params)
        return UserCreditsResponse(**result)
    
    def check_credits_by_owner_id(self, owner_id: str) -> UserCreditsSimpleResponse:
        """
        Check credits using owner_id from agent data
        
        Args:
            owner_id: Owner ID (typically from agent.owner_id)
        """
        result = self._request("GET", f"/credits/check/{owner_id}")
        return UserCreditsSimpleResponse(**result)

    # ===== NEW: PHONE NUMBERS =====
    def get_user_phone_numbers(self) -> List[PhoneNumber]:
        """Get all phone numbers assigned to the user"""
        result = self._request("GET", "/phone-numbers")
        return [PhoneNumber(**phone) for phone in result]

    # ===== CONVERSATION METHODS - SAME AS BEFORE =====
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

    # ===== USAGE & ANALYTICS - UPDATED =====
    def get_usage(
        self,
        period: str = "month",
        from_date: Optional[str] = None,
        to_date: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get API usage statistics"""
        params = {"period": period}
        if from_date:
            params["from_date"] = from_date
        if to_date:
            params["to_date"] = to_date
            
        return self._request("GET", "/usage", params=params)
    
    def get_credit_balance(self) -> Dict[str, Any]:
        """Get current credit balance (legacy - use get_credits_detailed instead)"""
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