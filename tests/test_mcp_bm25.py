"""
Advanced test script that forces multiple tool calls to the MCP retrieval server.

The query is intentionally complex and multi-part so the model must search
several times before it can compose a final answer.

Usage:
    1. Start the MCP server (in a separate terminal):
        export JAVA_HOME=$(ls -d ~/amazon-corretto-*)
        export PATH=$JAVA_HOME/bin:$PATH
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
        source .venv/bin/activate
        ANTHROPIC_API_KEY=<your_key> python test_mcp_bm25.py \
            --mcp-url "http://100.113.79.3:8080/mcp/"

Arguments:
    --mcp-url   (required) URL of the running MCP server.
    --model     Anthropic model to use (default: claude-sonnet-4-20250514).
    --budget    Thinking token budget (default: 4096).

Environment variables:
    ANTHROPIC_API_KEY   Your Anthropic API key (required).
"""
import argparse
import json
import os
import time

from anthropic import Anthropic

MCP_BETA = "mcp-client-2025-04-04"

# A multi-hop, reasoning-intensive query in the style of BrowseComp-Plus.
# It requires several independent searches to piece together the full answer.
QUERY = (
    "I'm trying to identify a specific person and event using the following clues. "
    "Please search for each clue separately and reason across the results:\n\n"
    "1. Search for the scientist who first proposed the concept of 'information entropy' "
    "and find what year they published their foundational paper.\n"
    "2. Search for what major world event was happening in that same year that could have "
    "influenced research priorities in communications and cryptography.\n"
    "3. Search for the institution or laboratory where this scientist was working at the time "
    "of the publication, and find one other notable researcher who worked there around the same period.\n\n"
    "After searching for each clue, synthesize the information into a short structured answer."
)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mcp-url", required=True)
    parser.add_argument("--model", default="claude-sonnet-4-20250514")
    parser.add_argument("--budget", type=int, default=4096)
    args = parser.parse_args()

    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise RuntimeError("ANTHROPIC_API_KEY not set")

    client = Anthropic(api_key=api_key)

    print("=" * 60)
    print(f"Model:   {args.model}")
    print(f"MCP URL: {args.mcp_url}")
    print(f"Query:\n{QUERY}")
    print("=" * 60)

    start = time.time()

    response = client.beta.messages.create(
        model=args.model,
        max_tokens=8192,
        thinking={"type": "enabled", "budget_tokens": args.budget},
        messages=[{"role": "user", "content": QUERY}],
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

    elapsed = time.time() - start

    # ── Parse and display output ──────────────────────────────────────────────
    tool_calls = []
    thinking_blocks = []
    answer = ""

    for block in response.content:
        if block.type == "thinking":
            thinking_blocks.append(block.thinking)

        elif block.type == "mcp_tool_use":
            tool_calls.append({"name": block.name, "input": block.input})
            print(f"\n[Tool call #{len(tool_calls)}] {block.name}")
            print(f"  Input: {json.dumps(block.input, indent=4)}")

        elif block.type == "mcp_tool_result":
            content_str = ""
            if isinstance(block.content, list):
                for part in block.content:
                    if hasattr(part, "text"):
                        content_str += part.text
            else:
                content_str = str(block.content)
            print(f"  Result (first 300 chars): {content_str[:300]}...")

        elif block.type == "text":
            answer += block.text

    print("\n" + "=" * 60)
    print("[Final Answer]")
    print(answer)
    print("=" * 60)
    print(f"\nSummary:")
    print(f"  Tool calls made : {len(tool_calls)}")
    print(f"  Thinking blocks : {len(thinking_blocks)}")
    print(f"  Stop reason     : {response.stop_reason}")
    print(f"  Tokens used     : input={response.usage.input_tokens}, output={response.usage.output_tokens}")
    print(f"  Elapsed         : {elapsed:.1f}s")


if __name__ == "__main__":
    main()
