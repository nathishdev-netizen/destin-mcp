#!/usr/bin/env python3
"""Test MCP server connection and functionality."""

import asyncio
import aiohttp
import json

async def test_mcp_server():
    """Test the MCP server endpoints."""
    base_url = "https://uninventive-davin-semihistorically.ngrok-free.dev"
    
    async with aiohttp.ClientSession() as session:
        print("🔍 Testing MCP Server Connection...")
        
        # Test 1: Health check
        print("\n1. Testing health endpoint...")
        async with session.get(f"{base_url}/health") as resp:
            if resp.status == 200:
                data = await resp.json()
                print(f"✅ Health check: {data}")
            else:
                print(f"❌ Health check failed: {resp.status}")
        
        # Test 2: Server info (GET)
        print("\n2. Testing server info (GET)...")
        async with session.get(f"{base_url}/mcp-v1") as resp:
            if resp.status == 200:
                data = await resp.json()
                print(f"✅ Server info: {data['name']} v{data['version']}")
            else:
                print(f"❌ Server info failed: {resp.status}")
        
        # Test 3: Initialize
        print("\n3. Testing MCP initialize...")
        init_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": True}
            }
        }
        
        async with session.post(
            f"{base_url}/mcp-v1",
            json=init_request,
            headers={"Content-Type": "application/json"}
        ) as resp:
            if resp.status == 200:
                data = await resp.json()
                print(f"✅ Initialize: Protocol {data['result']['protocolVersion']}")
            else:
                print(f"❌ Initialize failed: {resp.status}")
        
        # Test 4: List tools
        print("\n4. Testing tools/list...")
        tools_request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list",
            "params": {}
        }
        
        async with session.post(
            f"{base_url}/mcp-v1",
            json=tools_request,
            headers={"Content-Type": "application/json"}
        ) as resp:
            if resp.status == 200:
                data = await resp.json()
                tools = data['result']['tools']
                print(f"✅ Tools list: {len(tools)} tools available")
                for tool in tools:
                    print(f"   - {tool['name']}: {tool['title']}")
            else:
                print(f"❌ Tools list failed: {resp.status}")
        
        # Test 5: Test a tool call
        print("\n5. Testing hotel search tool...")
        search_request = {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": "search_hotels",
                "arguments": {
                    "country": "IN",
                    "cityCode": "DEL",
                    "fromDate": "2025-12-15",
                    "toDate": "2025-12-17",
                    "occupancy": [{"adults": 2, "roomCount": 1}],
                    "currency": "EUR",
                    "supplier": "dida"
                }
            }
        }
        
        async with session.post(
            f"{base_url}/mcp-v1",
            json=search_request,
            headers={"Content-Type": "application/json"}
        ) as resp:
            if resp.status == 200:
                data = await resp.json()
                if 'result' in data and 'content' in data['result']:
                    content = data['result']['content'][0]['text']
                    if "Found" in content and "hotels" in content:
                        print("✅ Hotel search: Working correctly")
                        # Show first few lines
                        lines = content.split('\n')[:5]
                        for line in lines:
                            if line.strip():
                                print(f"   {line}")
                    else:
                        print(f"⚠️  Hotel search: Unexpected response format")
                else:
                    print(f"❌ Hotel search: Invalid response structure")
            else:
                print(f"❌ Hotel search failed: {resp.status}")
        
        print("\n🎉 MCP Server Test Complete!")

if __name__ == "__main__":
    asyncio.run(test_mcp_server())
