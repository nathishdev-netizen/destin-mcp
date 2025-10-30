#!/bin/bash

echo "🔍 Testing MCP Server Connection..."
BASE_URL="https://uninventive-davin-semihistorically.ngrok-free.dev"

echo ""
echo "1. Testing health endpoint..."
curl -s "$BASE_URL/health" | jq '.'

echo ""
echo "2. Testing server info (GET)..."
curl -s "$BASE_URL/mcp-v1" | jq '.name, .version'

echo ""
echo "3. Testing MCP initialize..."
curl -s -X POST "$BASE_URL/mcp-v1" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{"tools":true}}}' \
  | jq '.result.protocolVersion, .result.serverInfo.name'

echo ""
echo "4. Testing tools/list..."
curl -s -X POST "$BASE_URL/mcp-v1" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":2,"method":"tools/list","params":{}}' \
  | jq '.result.tools | length'

echo ""
echo "5. Testing logging/setLevel (Inspector's first request)..."
curl -s -X POST "$BASE_URL/mcp-v1" \
  -H "Content-Type: application/json" \
  -d '{"method":"logging/setLevel","params":{"level":"debug"},"jsonrpc":"2.0","id":1}' \
  | jq '.'

echo ""
echo "🎉 MCP Server Test Complete!"
