# CallWhiz Python SDK

[![PyPI version](https://badge.fury.io/py/callwhiz.svg)](https://badge.fury.io/py/callwhiz)
[![Python Support](https://img.shields.io/pypi/pyversions/callwhiz.svg)](https://pypi.org/project/callwhiz/)

The official Python SDK for [CallWhiz](https://callwhiz.ai) - AI-powered voice agents for phone calls.

## Features

- 🤖 **Agent Management** - Create and manage AI voice agents
- 📞 **Call Control** - Initiate and manage voice calls  
- 🔗 **Webhooks** - Real-time call events and notifications
- 📊 **Analytics** - Usage tracking and conversation insights
- 🎙️ **Multi-Provider** - Support for OpenAI, ElevenLabs, Anthropic, and more

## Installation

```bash
pip install callwhiz
```

## Quick Start

```python
from callwhiz import CallWhiz

# Initialize client
client = CallWhiz(api_key="cw_your_api_key_here", sandbox=True)

# Create an agent
agent = client.create_agent(
    name="Support Agent",
    voice={"provider": "openai", "voice_id": "alloy"},
    llm={"provider": "openai", "model": "gpt-4"},
    prompt="You are a helpful customer support agent."
)

# Start a call
call = client.start_call(
    agent_id=agent.id,
    phone_number="+1234567890",
    context={"customer_name": "John Doe"}
)

print(f"Call started: {call.call_id}")
```

## Authentication

Get your API key from the [CallWhiz Dashboard](https://dashboard.callwhiz.ai):

```python
# Sandbox (for testing)
client = CallWhiz(api_key="cw_test_...", sandbox=True)

# Production  
client = CallWhiz(api_key="cw_live_...", sandbox=False)
```

## Documentation

- [Full Documentation](https://docs.callwhiz.ai)
- [API Reference](https://docs.callwhiz.ai/api)
- [Examples](https://github.com/zingaroai/callwhiz-python/tree/main/examples)

## Support

- 📧 Email: developers@callwhiz.ai
- 💬 Discord: [Join our community](https://discord.gg/callwhiz)
- 🐛 Issues: [GitHub Issues](https://github.com/zingaroai/callwhiz-python/issues)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.