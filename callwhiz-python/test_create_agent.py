
from callwhiz import CallWhiz

client = CallWhiz(api_key="cw_test_ACk0txhUbB52Gt1Y2s8gYfS2gLbIiTrl", sandbox=True)

try:
    agent = client.create_agent(
        name="My Complete Agent",
        voice={
            "provider": "openai",
            "voice_id": "alloy",
            "speed": 1.0,
            "pitch": 1.0
        },
        llm={
            "provider": "openai",
            "model": "gpt-4",
            "temperature": 0.7,
            "max_tokens": 150
        },
        prompt="You are a helpful customer service agent. Be friendly and professional.",
        description="AI agent for customer support with advanced settings",
        first_message="Hello! Welcome to our service. How can I help you today?",
        settings={
            "max_call_duration": 1800,
            "enable_interruptions": True,
            "silence_timeout": 5,
            "response_delay": 0.5
        }
    )
    
    print("✅ Agent created successfully!")
    print(f"   ID: {agent.id}")
    print(f"   Name: {agent.name}")
    print(f"   Status: {agent.status}")
    
except Exception as e:
    print(f"❌ Error: {e}")

client.close()