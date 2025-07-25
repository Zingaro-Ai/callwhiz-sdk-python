# #!/usr/bin/env python3
# """
# Simple CallWhiz Agent Creation Script
# """

from callwhiz import CallWhiz

# Configuration
API_KEY = "cw_live_5z2AS5vLn9zHjsG1JWuoPmGerDVgMLWJ"  # Replace with your API key
BASE_URL = "http://localhost:9000/v1"

def create_agent():
    """Create a simple agent"""
    
    # Initialize client
    client = CallWhiz(api_key=API_KEY, base_url=BASE_URL)
    
    # Create agent
    agent = client.create_agent(
        name="My Vinay Agent",
        model="nano",  # "lite", "nano", or "pro"
        voice="Calvin",  # Voice name
        language="en",  # Language code
        accent="American",  # Accent (for English)
        prompt="You are a helpful customer service agent.",
        first_message="Hello! How can I help you today?",
        description="A simple customer service agent"
    )
    
    print("✅ Agent created successfully!")
    print(f"Agent ID: {agent.id}")
    print(f"Name: {agent.name}")
    print(f"Voice: {agent.voice}")
    print(f"Model: {agent.model}")
    print(f"Language: {agent.language}")
    
    return agent.id

if __name__ == "__main__":
    try:
        agent_id = create_agent()
        print(f"\n🎉 Done! Agent ID: {agent_id}")
    except Exception as e:
        print(f"❌ Error: {e}")



# #!/usr/bin/env python3

# from callwhiz import CallWhiz
# import json

# def list_all_agents():
#     # Initialize the client with your API key
#     api_key = "cw_live_Ftp1LTmndBXzy52Sxeywm3atSxMzgXDD"  # Replace with your actual API key
#     base_url = "http://localhost:9000/v1"  # Update if different
    
#     try:
#         # Create client instance
#         client = CallWhiz(api_key=api_key, base_url=base_url)
        
#         # List all agents (default: page 1, limit 20)
#         print("Fetching agents...")
#         agents = client.list_agents()
        
#         print(f"\nFound {len(agents)} agents:")
#         print("=" * 50)
        
#         for i, agent in enumerate(agents, 1):
#             print(f"\n{i}. Agent ID: {agent.id}")
#             print(f"   Name: {agent.name}")
#             print(f"   Model: {agent.model}")
#             print(f"   Voice: {agent.voice}")
#         client.close()
        
#     except Exception as e:
#         print(f"Error: {e}")

# def list_agents_with_filters():
#     """List agents with custom filters"""
#     api_key = "cw_live_Ftp1LTmndBXzy52Sxeywm3atSxMzgXDD"  # Replace with your actual API key
#     base_url = "http://localhost:9000/v1"
    
#     try:
#         client = CallWhiz(api_key=api_key, base_url=base_url)
        
#         # List active agents only
#         active_agents = client.list_agents(status="active")
#         print(f"Active agents: {len(active_agents)}")
        
#         # List with custom pagination
#         more_agents = client.list_agents(page=1, limit=50)
#         print(f"Agents (limit 50): {len(more_agents)}")
        
#         # List inactive agents
#         inactive_agents = client.list_agents(status="inactive")
#         print(f"Inactive agents: {len(inactive_agents)}")
        
#         client.close()
        
#     except Exception as e:
#         print(f"Error: {e}")

# def list_agents_json():
#     """List agents and output as JSON"""
#     api_key = "cw_live_Ftp1LTmndBXzy52Sxeywm3atSxMzgXDD"  # Replace with your actual API key
#     base_url = "http://localhost:9000/v1"
    
#     try:
#         client = CallWhiz(api_key=api_key, base_url=base_url)
#         agents = client.list_agents()
        
#         # Convert to dict for JSON serialization
#         agents_data = []
#         for agent in agents:
#             agent_dict = {
#                 "id": agent.id,
#                 "name": agent.name,
#                 "model": agent.model,
#                 "voice": agent.voice,
#                 "status": getattr(agent, 'status', None),
#                 "language": getattr(agent, 'language', None),
#                 "description": getattr(agent, 'description', None),
#                 "created_at": getattr(agent, 'created_at', None),
#                 "updated_at": getattr(agent, 'updated_at', None)
#             }
#             agents_data.append(agent_dict)
        
#         print(json.dumps(agents_data, indent=2, default=str))
#         client.close()
        
#     except Exception as e:
#         print(f"Error: {e}")

# if __name__ == "__main__":
#     # Basic listing
#     list_all_agents()
    
#     print("\n" + "="*60 + "\n")
    
#     # With filters
#     print("FILTERED RESULTS:")
#     list_agents_with_filters()
    
#     print("\n" + "="*60 + "\n")
    
#     # JSON output
#     print("JSON OUTPUT:")
#     list_agents_json()