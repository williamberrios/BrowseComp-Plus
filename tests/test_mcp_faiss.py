"""
Quick test script to verify the MCP retrieval server is working with the Anthropic API.

Usage:
    1. Start the MCP server (in a separate terminal):
        source .venv/bin/activate
        python searcher/mcp_server.py \\
            --searcher-type faiss \\
            --index-path "indexes/qwen3-embedding-8b/corpus.shard*.pkl" \\
            --model-name "Qwen/Qwen3-Embedding-8B" \\
            --normalize \\
            --port 8080 \\
            --public

    2. Copy the public ngrok URL printed by the server, e.g.:
            https://xxxx.ngrok-free.app/mcp

    3. Run this script:
        ANTHROPIC_API_KEY=<your_key> python test_mcp_faiss.py --mcp-url "https://xxxx.ngrok-free.app/mcp" --query "What is the capital of France?"

Arguments:
    --mcp-url   (required) Public URL of the running MCP server.
    --query     Question to ask (default: "What is the capital of France?").
    --model     Anthropic model to use (default: claude-sonnet-4-20250514).

Environment variables:
    ANTHROPIC_API_KEY   Your Anthropic API key (required).
"""
import argparse
import os

from anthropic import Anthropic

MCP_BETA = "mcp-client-2025-04-04"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mcp-url", required=True)
    parser.add_argument("--query", default="What is the capital of France?")
    parser.add_argument("--model", default="claude-sonnet-4-20250514")
    args = parser.parse_args()

    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise RuntimeError("ANTHROPIC_API_KEY not set")

    client = Anthropic(api_key=api_key)

    print(f"Sending query: {args.query}")
    print(f"MCP URL: {args.mcp_url}")
    print(f"Model: {args.model}")
    print("---")

    response = client.beta.messages.create(
        model=args.model,
        max_tokens=2048,
        messages=[{"role": "user", "content": args.query}],
        mcp_servers=[
            {
                "type": "url",
                "url": args.mcp_url,
                "name": "search-server",
                "tool_configuration": {"enabled": True},
            }
        ],
        extra_headers={"anthropic-beta": MCP_BETA},
    )

    for block in response.content:
        if block.type == "text":
            print("[Answer]", block.text)
        elif block.type == "mcp_tool_use":
            print(f"[Tool call] {block.name}({block.input})")
        elif block.type == "mcp_tool_result":
            print(str(block.content))

    print("---")
    print(f"Stop reason: {response.stop_reason}")
    print(f"Tokens used: input={response.usage.input_tokens}, output={response.usage.output_tokens}")


if __name__ == "__main__":
    main()
