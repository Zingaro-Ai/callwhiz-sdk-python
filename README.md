# CallWhiz Python SDK

[![PyPI version](https://badge.fury.io/py/callwhiz.svg)](https://badge.fury.io/py/callwhiz) 
[![Python Support](https://img.shields.io/pypi/pyversions/callwhiz.svg)](https://pypi.org/project/callwhiz/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Downloads](https://img.shields.io/pypi/dm/callwhiz.svg)](https://pypi.org/project/callwhiz/)

The official Python SDK for [CallWhiz](https://callwhiz.ai) - AI-powered voice agents for phone calls with advanced conversation flows and real-time capabilities.

## ✨ Features

- 🤖 **Agent Management** - Create and manage AI voice agents with multi-stage conversations
- 📞 **Call Control** - Initiate and manage voice calls with real-time monitoring
- 💰 **Credits Management** - Check account balance and usage analytics
- 🔗 **Webhooks & Functions** - Real-time events and custom agent functions
- 📊 **Analytics** - Usage tracking, conversation insights, and transcripts
- 🎭 **Multi-Stage Agents** - Complex conversation flows with stage transitions
- 🌍 **Multi-Language** - Support for English, Spanish, Hindi, Telugu, and more
- 🎙️ **Multiple Voices** - Various voice options with accent customization

## 🚀 Installation

```bash
pip install callwhiz
```

## ⚡ Quick Start

```python
from callwhiz import CallWhiz

# Initialize client with Bearer authentication
client = CallWhiz(
    api_key="cw_test_your_api_key_here",
    base_url="http://localhost:9000/v1"  # or your API endpoint
)

# Check your credits first
credits = client.get_credits_simple()
print(f"Credits: {credits.credits_remaining}/{credits.total_credits}")

# Create a simple agent
agent = client.create_agent(
    name="Customer Support Agent",
    model="nano",  # "lite", "nano", or "pro"
    voice="Olivia",  # Voice name
    language="en",  # Language code
    accent="American",  # For English voices
    prompt="You are a helpful customer support agent.",
    first_message="Hello! How can I help you today?"
)

# Start a call
call = client.start_call(
    agent_id=agent.id,
    phone_number="+1234567890",
    context={
        "customer_name": "John Doe",
        "customer_id": "CUST-001",
        "purpose": "Support inquiry"
    }
)

print(f"Call started: {call.call_id} - Status: {call.status}")
```

## 🔐 Authentication

Get your API key from the [CallWhiz Dashboard](https://callwhiz.ai/dashboard):

```python
# Sandbox/Test Environment
client = CallWhiz(
    api_key="cw_test_...",  # Test API key
    base_url="http://localhost:9000/v1"
)

# Production Environment
client = CallWhiz(
    api_key="cw_live_...",  # Live API key
    base_url="https://api.callwhiz.ai/v1"
)
```

## 💰 Credits Management

Monitor and check your account credits:

```python
# Simple credits check
credits = client.get_credits_simple()
print(f"Remaining: {credits.credits_remaining}")
print(f"Usage: {credits.usage_percentage}%")

# Detailed credits with billing info
detailed = client.get_credits_detailed()
print(f"Plan: {detailed.plan_id}")
print(f"Next renewal: {detailed.next_renewal_date}")

# Check credits by owner ID (from agent data)
owner_credits = client.check_credits_by_owner_id(owner_id)
```

## 🎭 Multi-Stage Agents

Create agents with complex conversation flows:

```python
from callwhiz import CallStage

# Define conversation stages
stages = [
    CallStage(
        name="greeting",
        prompt="Greet the customer and ask how you can help them today."
    ),
    CallStage(
        name="assistance", 
        prompt="Help the customer with their request. Be thorough and helpful."
    ),
    CallStage(
        name="closing",
        prompt="Summarize the conversation and thank the customer."
    )
]

# Create multi-stage agent
agent = client.create_agent(
    name="Multi-Stage Support Agent",
    model="lite",
    voice="Brian",
    language="en",
    accent="British",
    stages=stages,  # Use stages instead of prompt
    description="Advanced support agent with conversation flow"
)
```

## 🔗 User Webhooks (Functions)

Create custom functions that your agents can call:

```python
# Create a webhook function
weather_function = client.create_user_webhook(
    name="get_weather",
    description="Get current weather for a location",
    endpoint="https://api.openweathermap.org/data/2.5/weather",
    method="GET",
    parameters={
        "q": {
            "type": "string",
            "description": "City name",
            "required": True,
            "examples": ["New York", "London", "Tokyo"]
        },
        "units": {
            "type": "string",
            "description": "Temperature units",
            "enum": ["metric", "imperial"],
            "default": "metric"
        }
    },
    auth_type="api_key",
    auth_header_name="appid",
    auth_value="your_openweather_api_key"
)

# Create agent with function access
agent = client.create_agent(
    name="Weather Assistant",
    model="nano",
    voice="Eric",
    language="en",
    prompt="You can check weather using the get_weather function.",
    webhook_ids=[weather_function.id]
)
```

## 📞 Phone Numbers

Get your assigned phone numbers:

```python
phones = client.get_user_phone_numbers()
for phone in phones:
    print(f"Number: {phone.phone_number}")
    print(f"Max channels: {phone.max_channels}")
```

## 📊 Usage Analytics

Track your API usage and call analytics:

```python
# Get usage statistics
usage = client.get_usage(period="week")
print(f"API calls: {usage['api_calls']['total']}")
print(f"Voice calls: {usage['voice_calls']['total']}")

# Get call transcript
transcript = client.get_call_transcript(call_id)
for entry in transcript.transcript:
    print(f"{entry.speaker}: {entry.text}")

# Get call recording
recording = client.get_call_recording(call_id)
print(f"Recording URL: {recording.recording_url}")
```

## 🔄 Migration from v1.x

If you're upgrading from SDK v1.x, see our [Migration Guide](MIGRATION_GUIDE.md) for step-by-step instructions.

**Key Changes in v2.0.0:**
- Authentication changed to Bearer token
- Simplified agent creation structure
- New credits management API
- Multi-stage agent support
- User webhooks for custom functions

## 📚 Advanced Examples

### Complete Call Workflow

```python
from callwhiz import CallWhiz

with CallWhiz(api_key="cw_test_...", base_url="http://localhost:9000/v1") as client:
    # Check credits before starting
    credits = client.get_credits_simple()
    if credits.credits_remaining < 1:
        print("Insufficient credits!")
        exit(1)
    
    # Create agent
    agent = client.create_agent(
        name="Sales Agent",
        model="nano",
        voice="Calvin",
        language="en",
        prompt="You are a professional sales agent.",
        description="Handles sales inquiries"
    )
    
    # Start call with context
    call = client.start_call(
        agent_id=agent.id,
        phone_number="+1234567890",
        context={
            "lead_source": "website",
            "product_interest": "premium_plan",
            "customer_score": 85
        },
        metadata={"campaign": "q4_sales"}
    )
    
    # Monitor call status
    status = client.get_call(call.call_id)
    print(f"Call status: {status.status}")
    
    # Cleanup
    client.delete_agent(agent.id)
```

### Error Handling

```python
from callwhiz import CallWhiz
from callwhiz.exceptions import CallWhizError, AuthenticationError, RateLimitError

try:
    client = CallWhiz(api_key="invalid_key")
    agent = client.create_agent(
        name="Test Agent",
        model="nano",
        voice="Calvin",
        language="en",
        prompt="Test"
    )
except AuthenticationError:
    print("Invalid API key")
except RateLimitError:
    print("Rate limit exceeded")
except CallWhizError as e:
    print(f"API error: {e}")
```

## 🛠️ Development

### Running Tests

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run unit tests
pytest tests/unit/

# Run integration tests (requires API server)
pytest tests/integration/

# Run with coverage
pytest --cov=callwhiz tests/
```

### Code Formatting

```bash
# Format code
black callwhiz/ tests/

# Lint code
ruff callwhiz/ tests/

# Type checking
mypy callwhiz/
```

## 🌐 Language Support

Supported languages and regions:

| Language | Code | Accents Available |
|----------|------|-------------------|
| English | `en` | American, British |
| Spanish | `es` | Standard |
| Hindi | `hi` | Standard |
| Telugu | `te` | Standard |

## 🎙️ Available Voices

Popular voice options:
- **Calvin** - Male, professional
- **Olivia** - Female, friendly  
- **Brian** - Male, British accent
- **Nova** - Female, energetic
- **Echo** - Neutral, clear

## 📖 Documentation

- [Full Documentation](https://docs.callwhiz.ai/sdk/python)
- [API Reference](https://docs.callwhiz.ai/api)
- [Migration Guide](MIGRATION_GUIDE.md)
- [Examples Repository](https://github.com/zingaroai/callwhiz-python/tree/main/examples)
- [Changelog](CHANGELOG.md)

## 🤝 Support

- 📧 **Email**: developers@callwhiz.ai
- 💬 **Discord**: [Join our community](https://discord.gg/callwhiz)
- 🐛 **Issues**: [GitHub Issues](https://github.com/zingaroai/callwhiz-python/issues)
- 📚 **Docs**: [Documentation Portal](https://docs.callwhiz.ai)
- 🎯 **Status**: [API Status](https://status.callwhiz.ai)

## 🏢 Enterprise

For enterprise features and support:
- 📞 **Sales**: sales@callwhiz.ai
- 🏗️ **Custom Integration**: enterprise@callwhiz.ai
- 📋 **SLA & Support**: Available for enterprise plans

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

---

**Made with ❤️ by [Zingaro AI LLC](https://zingaroai.com)**

*CallWhiz SDK v2.0.0 - Powering the future of AI voice interactions*