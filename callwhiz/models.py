# callwhiz/models.py - UPDATED FOR v2.0.0
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel


# ===== NEW: CALL STAGE MODEL FOR MULTI-STAGE AGENTS =====
class CallStage(BaseModel):
    """Call stage for multi-stage agents"""
    name: str
    prompt: str
    webhook_ids: Optional[List[str]] = None


# ===== UPDATED: SIMPLIFIED AGENT MODEL =====
class Agent(BaseModel):
    """Updated Agent model to match new API structure"""
    id: str
    name: str
    description: Optional[str] = None
    model: str  # "lite", "nano", "pro"
    voice: str  # Voice name like "Calvin", "Olivia", "Brian"
    language: str  # "en", "es", "hi", "te"
    accent: Optional[str] = None  # "American", "British"
    status: str  # "active", "inactive", "draft"
    created_at: datetime
    updated_at: datetime
    webhook_ids: List[str] = []
    has_stages: bool = False
    stage_count: int = 0

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }


# ===== CALL MODELS - UPDATED =====
class Call(BaseModel):
    """Updated Call model"""
    call_id: str
    status: str
    agent_id: str
    phone_number: str
    created_at: datetime
    estimated_cost: Optional[float] = None
    started_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None
    duration: Optional[int] = None
    cost: Optional[float] = None
    outcome: Optional[str] = None
    transcript_available: bool = False
    recording_available: bool = False
    context: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }


# ===== WEBHOOK MODELS - SAME BUT UPDATED =====
class WebhookRetryPolicy(BaseModel):
    max_retries: int = 3
    retry_delay: int = 60


class Webhook(BaseModel):
    """System webhook model"""
    webhook_id: str
    url: str
    events: List[str]
    agent_ids: List[str] = []
    active: bool = True
    created_at: datetime
    secret: Optional[str] = None  # Only on creation
    retry_policy: Optional[WebhookRetryPolicy] = None
    headers: Optional[Dict[str, str]] = None

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }


# ===== NEW: USER WEBHOOK MODELS =====
class ParameterDefinition(BaseModel):
    """Parameter definition for user webhooks"""
    type: str  # "string", "number", "boolean", "array", "object"
    description: str
    required: bool = False
    default: Optional[Any] = None
    # Additional JSON Schema fields
    title: Optional[str] = None
    examples: Optional[List[Any]] = None
    enum: Optional[List[Any]] = None
    minLength: Optional[int] = None
    maxLength: Optional[int] = None
    minimum: Optional[float] = None
    maximum: Optional[float] = None
    items: Optional[Dict[str, Any]] = None
    properties: Optional[Dict[str, Any]] = None


class UserWebhook(BaseModel):
    """User webhook (function) that agents can call"""
    id: str
    name: str
    description: str
    endpoint: str
    method: str
    parameters: Dict[str, ParameterDefinition] = {}
    created_at: datetime
    updated_at: Optional[datetime] = None
    auth_type: str = "none"  # "none", "api_key", "bearer"
    has_auth: bool = False

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }


# ===== NEW: CREDITS MODELS =====
class UserCreditsSimpleResponse(BaseModel):
    """Simple credits response"""
    credits_remaining: float
    total_credits: int
    usage_percentage: float


class UserCreditsResponse(BaseModel):
    """Detailed credits response"""
    user_id: str
    email: str
    credits_remaining: float
    monthly_credits: int
    total_credits: int
    plan_id: str
    billing_active: bool
    next_renewal_date: Optional[datetime] = None
    created_at: datetime

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }


# ===== NEW: PHONE NUMBER MODEL =====
class PhoneNumber(BaseModel):
    """Phone number with channel limit"""
    phone_number: str
    max_channels: int


# ===== TRANSCRIPT & RECORDING MODELS - UPDATED =====
class TranscriptEntry(BaseModel):
    timestamp: datetime
    speaker: str  # "agent" or "customer"
    text: str

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }


class TranscriptResponse(BaseModel):
    call_id: str
    transcript: List[TranscriptEntry]
    summary: Optional[str] = None
    duration: int
    word_count: int


class RecordingResponse(BaseModel):
    call_id: str
    recording_url: str
    duration: int
    format: str
    size_bytes: int
    expires_at: datetime

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }


# ===== CONVERSATION MODELS - SAME AS BEFORE =====
class ConversationMessage(BaseModel):
    timestamp: datetime
    speaker: str
    text: str
    audio_duration: float

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }


class ConversationSummary(BaseModel):
    conversation_id: str
    call_id: str
    agent_id: str
    phone_number: str
    started_at: datetime
    ended_at: Optional[datetime]
    duration: int
    message_count: int
    summary: Optional[str]
    outcome: str

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }


class ConversationDetail(BaseModel):
    conversation_id: str
    call_id: str
    agent_id: str
    phone_number: str
    started_at: datetime
    ended_at: Optional[datetime]
    duration: int
    messages: List[ConversationMessage]
    summary: Optional[str]
    outcome: str
    metadata: Optional[Dict[str, Any]]

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }


# ===== USAGE & ANALYTICS MODELS - SAME AS BEFORE =====
class UsageStats(BaseModel):
    period: str
    from_date: datetime
    to_date: datetime
    api_calls: Dict[str, Any]
    voice_calls: Dict[str, Any]
    rate_limits: Dict[str, Any]

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }


class CreditBalance(BaseModel):
    balance: float
    currency: str
    low_balance_threshold: float
    auto_recharge_enabled: bool
    last_recharged_at: Optional[datetime]
    usage_this_month: float

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }


class AccountLimits(BaseModel):
    plan: str
    limits: Dict[str, Any]
    current_usage: Dict[str, Any]


# ===== LEGACY MODELS (REMOVED) =====
# VoiceConfig, LLMConfig, AgentSettings - These are removed in v2.0.0
# Use the simplified Agent model instead