"""
Small LangChain example using the BrowseComp+ MCP server (streamable-http).

Install dependencies first:
    uv pip install langchain-mcp-adapters langchain-anthropic langgraph

Usage:
    1. Start the MCP server (in a separate terminal):
        source .venv/bin/activate
        python searcher/mcp_server.py \
            --searcher-type bm25 \
            --index-path indexes/bm25 \
            --port 8080 \
            --host 0.0.0.0 \
            --public \
            --transport streamable-http

    2. Get the MCP URL. Pick one depending on your setup:
        - Local access:     http://127.0.0.1:8080/mcp/
        - Tailscale access: http://<tailscale-ip>:8080/mcp/
                            e.g. http://100.113.79.3:8080/mcp/
                            or   http://<machine-name>.<tailnet>.ts.net:8080/mcp/
        - Public (ngrok):   https://xxxx.ngrok-free.app/mcp
                            (printed by the server on startup)

        Note: --host 0.0.0.0 is required to accept connections from Tailscale or other
        external networks. Without it, the server only listens on 127.0.0.1.

    3. Run this script:
        conda activate wbr-mas
        ANTHROPIC_API_KEY=<your_key> python tests/test_mcp_langchain.py \
            --mcp-url "http://100.113.79.3:8080/mcp/" \
            --query "What is BM25?"
"""
import argparse
import asyncio
import os

from langchain_anthropic import ChatAnthropic
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent


async def main(mcp_url: str, query: str, model: str) -> None:
    llm = ChatAnthropic(model=model)

    client = MultiServerMCPClient(
        {
            "search": {
                "url": mcp_url,
                "transport": "streamable_http",
            }
        }
    )
    tools = await client.get_tools()
    print(f"Available tools: {[t.name for t in tools]}\n")

    agent = create_react_agent(llm, tools)

    response = await agent.ainvoke({"messages": [{"role": "user", "content": query}]})

    last_message = response["messages"][-1]
    print("Answer:", last_message.content)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--mcp-url", required=True, help="MCP server URL (e.g. https://xxxx.ngrok-free.dev/mcp)")
    parser.add_argument("--query", default="What is BM25 retrieval?", help="Question to ask")
    parser.add_argument("--model", default="claude-sonnet-4-6", help="Anthropic model")
    args = parser.parse_args()

    if not os.getenv("ANTHROPIC_API_KEY"):
        raise SystemExit("ANTHROPIC_API_KEY environment variable is not set.")

    asyncio.run(main(args.mcp_url, args.query, args.model))
