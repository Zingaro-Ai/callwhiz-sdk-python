# callwhiz/__init__.py
from .client import CallWhiz
from .exceptions import CallWhizError, AuthenticationError, NotFoundError, RateLimitError
from .models import (
    Agent, Call, Webhook,
    VoiceConfig, LLMConfig, AgentSettings,
    WebhookRetryPolicy, TranscriptEntry, Transcript, Recording,
    ConversationMessage, ConversationSummary, ConversationDetail,
    UsageStats, CreditBalance, AccountLimits
)

__version__ = "1.0.0"
__all__ = [
    # Client
    "CallWhiz",
    
    # Exceptions
    "CallWhizError", 
    "AuthenticationError", 
    "NotFoundError", 
    "RateLimitError",
    
    # Main Models
    "Agent", 
    "Call", 
    "Webhook",
    
    # Configuration Models
    "VoiceConfig", 
    "LLMConfig", 
    "AgentSettings",
    "WebhookRetryPolicy",
    
    # Data Models
    "TranscriptEntry", 
    "Transcript", 
    "Recording",
    "ConversationMessage", 
    "ConversationSummary", 
    "ConversationDetail",
    "UsageStats", 
    "CreditBalance", 
    "AccountLimits"
]