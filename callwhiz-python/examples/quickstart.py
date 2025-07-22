from callwhiz import CallWhiz

# Initialize client
client = CallWhiz(api_key="cw_test_your_key_here", sandbox=True)

# Create agent
agent = client.create_agent(
    name="Support Agent",
    voice={"provider": "openai", "voice_id": "alloy"},
    llm={"provider": "openai", "model": "gpt-4"},
    prompt="You are a helpful customer support agent."
)

# Start call
call = client.start_call(
    agent_id=agent.id,
    phone_number="+1234567890",
    context={"customer_name": "John Doe"}
)

print(f"Call started: {call.call_id}")
print(f"Status: {call.status}")