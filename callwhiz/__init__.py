# callwhiz/__init__.py - UPDATED FOR v2.0.0
from .client import CallWhiz
from .exceptions import CallWhizError, AuthenticationError, NotFoundError, RateLimitError
from .models import (
    # Core Models
    Agent, Call, Webhook,
    
    # New Models
    UserWebhook, CallStage, PhoneNumber,
    ParameterDefinition,
    
    # Credits Models
    UserCreditsResponse, UserCreditsSimpleResponse,
    
    # Transcript & Recording Models
    TranscriptEntry, TranscriptResponse, RecordingResponse,
    
    # Conversation Models
    ConversationMessage, ConversationSummary, ConversationDetail,
    
    # Analytics Models
    UsageStats, CreditBalance, AccountLimits,
    
    # Webhook Models
    WebhookRetryPolicy
)

__version__ = "2.0.0"
__all__ = [
    # Client
    "CallWhiz",
    
    # Exceptions
    "CallWhizError", 
    "AuthenticationError", 
    "NotFoundError", 
    "RateLimitError",
    
    # Core Models
    "Agent", 
    "Call", 
    "Webhook",
    
    # New Models v2.0.0
    "UserWebhook",
    "CallStage", 
    "PhoneNumber",
    "ParameterDefinition",
    
    # Credits Models
    "UserCreditsResponse",
    "UserCreditsSimpleResponse",
    
    # Data Models
    "TranscriptEntry", 
    "TranscriptResponse", 
    "RecordingResponse",
    "ConversationMessage", 
    "ConversationSummary", 
    "ConversationDetail",
    "UsageStats", 
    "CreditBalance", 
    "AccountLimits",
    "WebhookRetryPolicy"
]