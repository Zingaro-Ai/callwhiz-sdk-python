# delete_agent.py - Script to delete a specific agent
from callwhiz import CallWhiz

# Initialize client
client = CallWhiz(api_key="cw_test_ACk0txhUbB52Gt1Y2s8gYfS2gLbIiTrl", sandbox=True)

try:
    # Get all agents
    agents = client.list_agents()
    
    if not agents:
        print("❌ No agents found to delete!")
        exit()
    
    # Show available agents
    print("📋 Available agents to delete:")
    print("=" * 50)
    
    for i, agent in enumerate(agents, 1):
        print(f"{i}. {agent.name}")
        print(f"   ID: {agent.id}")
        print(f"   Status: {agent.status}")
        print(f"   Calls: {agent.call_count}")
        print("-" * 30)
    
    # Ask user to choose
    choice = input(f"\nWhich agent to delete? (1-{len(agents)}) or 'q' to quit: ")
    
    if choice.lower() == 'q':
        print("❌ Cancelled deletion")
        exit()
    
    # Get selected agent
    agent_index = int(choice) - 1
    if agent_index < 0 or agent_index >= len(agents):
        print("❌ Invalid choice!")
        exit()
    
    selected_agent = agents[agent_index]
    
    # Confirm deletion
    confirm = input(f"\n⚠️  Are you sure you want to delete '{selected_agent.name}'? (yes/no): ")
    
    if confirm.lower() != 'yes':
        print("❌ Cancelled deletion")
        exit()
    
    # Delete the agent
    success = client.delete_agent(selected_agent.id)
    
    if success:
        print(f"✅ Agent '{selected_agent.name}' deleted successfully!")
        print(f"   (Agent ID: {selected_agent.id})")
    else:
        print("❌ Failed to delete agent")
        
except ValueError:
    print("❌ Please enter a valid number!")
except Exception as e:
    print(f"❌ Error deleting agent: {e}")

finally:
    client.close()