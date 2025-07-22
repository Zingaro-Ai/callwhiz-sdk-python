# list_agents.py - Simple script to list all agents
from callwhiz import CallWhiz

# Initialize client
client = CallWhiz(api_key="cw_test_ACk0txhUbB52Gt1Y2s8gYfS2gLbIiTrl", sandbox=True)

try:
    # List all agents
    agents = client.list_agents()
    
    print(f"📋 Found {len(agents)} agents:")
    print("=" * 50)
    
    for i, agent in enumerate(agents, 1):
        print(f"{i}. {agent.name}")
        print(f"   ID: {agent.id}")
        print(f"   Status: {agent.status}")
        print(f"   Description: {agent.description or 'No description'}")
        print(f"   Voice: {agent.voice.provider}/{agent.voice.voice_id}")
        print(f"   LLM: {agent.llm.provider}/{agent.llm.model}")
        print(f"   Calls: {agent.call_count}")
        print(f"   Created: {agent.created_at}")
        print("-" * 30)
    
    if not agents:
        print("No agents found. Create one first!")
        
except Exception as e:
    print(f"❌ Error listing agents: {e}")

finally:
    client.close()