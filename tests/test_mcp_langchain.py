"""
Small LangChain example using the BrowseComp+ MCP server (streamable-http).

Install dependencies first:
    uv pip install langchain-mcp-adapters langchain-anthropic langgraph

Usage:
conda activate wbr-mas
ANTHROPIC_API_KEY=<your_key> python tests/test_mcp_langchain.py --mcp-url "https://xxxx.ngrok-free.dev/mcp" --query "What is BM25?"
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
