# test_sdk.py
from callwhiz import CallWhiz

client = CallWhiz(
    api_key="cw_test_ACk0txhUbB52Gt1Y2s8gYfS2gLbIiTrl", 
    sandbox=True
)

try:
    agents = client.list_agents()
    print(f"✅ API connection works! Found {len(agents)} agents")
except Exception as e:
    print(f"❌ Error: {e}")

client.close()