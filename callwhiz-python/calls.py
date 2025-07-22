# call_agent.py - Simple script to make a call with an agent
from callwhiz import CallWhiz

# Initialize client
client = CallWhiz(api_key="cw_test_ACk0txhUbB52Gt1Y2s8gYfS2gLbIiTrl", sandbox=True)

try:
    # First, get available agents
    agents = client.list_agents()
    
    if not agents:
        print("❌ No agents found. Create an agent first!")
        exit()
    
    # Use the first agent
    agent = agents[0]
    print(f"🤖 Using agent: {agent.name} (ID: {agent.id})")
    
    # Start a call
    call = client.start_call(
        agent_id=agent.id,
        phone_number="+919014583641",  # Test phone number
        context={
            "customer_name": "John Doe",
            "customer_id": "CUST_12345",
            "purpose": "test_call"
        },
        metadata={
            "test": True,
            "source": "sdk_script"
        }
    )
    
    print("✅ Call initiated successfully!")
    print(f"   Call ID: {call.call_id}")
    print(f"   Status: {call.status}")
    print(f"   Agent: {call.agent_id}")
    print(f"   Phone: {call.phone_number}")
    print(f"   Estimated Cost: ${call.estimated_cost}")
    
except Exception as e:
    print(f"❌ Error making call: {e}")

finally:
    client.close()