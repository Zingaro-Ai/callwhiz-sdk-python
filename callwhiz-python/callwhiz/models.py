# callwhiz/models.py - COMPLETE VERSION
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel


class VoiceConfig(BaseModel):
    provider: str
    voice_id: str
    speed: float = 1.0
    pitch: float = 1.0


class LLMConfig(BaseModel):
    provider: str
    model: str
    temperature: float = 0.7
    max_tokens: int = 150


class AgentSettings(BaseModel):
    max_call_duration: int = 1800
    enable_interruptions: bool = True
    silence_timeout: int = 5
    response_delay: float = 0.5


class Agent(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    status: str
    created_at: datetime
    updated_at: datetime
    voice: VoiceConfig
    llm: LLMConfig
    settings: AgentSettings
    prompt: Optional[str] = None
    first_message: Optional[str] = None
    call_count: int = 0
    total_duration: int = 0


class Call(BaseModel):
    call_id: str
    status: str
    agent_id: str
    phone_number: str
    created_at: datetime
    started_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None
    duration: Optional[int] = None
    cost: Optional[float] = None
    outcome: Optional[str] = None
    transcript_available: bool = False
    recording_available: bool = False
    context: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None
    estimated_cost: Optional[float] = None


class WebhookRetryPolicy(BaseModel):
    max_retries: int = 3
    retry_delay: int = 60


class Webhook(BaseModel):
    webhook_id: str
    url: str
    events: List[str]
    agent_ids: List[str] = []
    active: bool = True
    created_at: datetime
    secret: Optional[str] = None  # Only on creation
    retry_policy: Optional[WebhookRetryPolicy] = None
    headers: Optional[Dict[str, str]] = None


class TranscriptEntry(BaseModel):
    timestamp: datetime
    speaker: str  # "agent" or "customer"
    text: str
    audio_duration: Optional[float] = None


class Transcript(BaseModel):
    call_id: str
    transcript: List[TranscriptEntry]
    summary: Optional[str] = None
    duration: int
    word_count: int


class Recording(BaseModel):
    call_id: str
    recording_url: str
    duration: int
    format: str
    size_bytes: int
    expires_at: datetime


class ConversationMessage(BaseModel):
    timestamp: datetime
    speaker: str
    text: str
    audio_duration: float


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


class UsageStats(BaseModel):
    period: str
    from_date: datetime
    to_date: datetime
    api_calls: Dict[str, Any]
    voice_calls: Dict[str, Any]
    rate_limits: Dict[str, Any]


class CreditBalance(BaseModel):
    balance: float
    currency: str
    low_balance_threshold: float
    auto_recharge_enabled: bool
    last_recharged_at: Optional[datetime]
    usage_this_month: float


class AccountLimits(BaseModel):
    plan: str
    limits: Dict[str, Any]
    current_usage: Dict[str, Any]