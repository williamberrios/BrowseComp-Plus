# Test Scripts Guide

This document explains how to run the MCP test scripts: `test_mcp_faiss.py`, `test_mcp_bm25.py`, and `test_mcp_langchain.py`.

## Prerequisites

Activate the virtual environment:
```bash
source .venv/bin/activate
```

If using BM25 (required for `test_mcp_bm25.py`), Java 21 must be installed. The no-sudo way is to download Amazon Corretto 21 directly to your home directory:

```bash
wget https://corretto.aws/downloads/latest/amazon-corretto-21-x64-linux-jdk.tar.gz
tar -xzf amazon-corretto-21-x64-linux-jdk.tar.gz -C ~/
```

Then set `JAVA_HOME`:
```bash
export JAVA_HOME=$(ls -d ~/amazon-corretto-*)
export PATH=$JAVA_HOME/bin:$PATH
```

Verify the installation:
```bash
java -version   # should show openjdk 21.x.x
```

---

## test_mcp_faiss.py

Simple test that sends a single query to the MCP retrieval server via the Anthropic API.

### 1. Start the MCP server (separate terminal)

```bash
source .venv/bin/activate
python searcher/mcp_server.py \
    --searcher-type faiss \
    --index-path "indexes/qwen3-embedding-8b/corpus.shard*.pkl" \
    --model-name "Qwen/Qwen3-Embedding-8B" \
    --normalize \
    --port 8080 \
    --public
```

### 2. Get the public URL

When the server starts it prints a line like:
```
Public MCP endpoint available at: https://xxxx.ngrok-free.app/mcp
```
Copy that URL and use it in the next step.

> **Note:** The ngrok URL is **not permanent** — it changes every time the server restarts (free tier).
> To get a stable URL, claim your free static domain at [dashboard.ngrok.com/domains](https://dashboard.ngrok.com/domains)
> and configure it in `~/.config/ngrok/ngrok.yml`.

### 3. Run the test

```bash
ANTHROPIC_API_KEY=<your_key> python tests/test_mcp_faiss.py \
    --mcp-url "https://xxxx.ngrok-free.app/mcp" \
    --query "What is the capital of France?"
```

**Arguments:**

| Argument | Required | Default | Description |
|----------|----------|---------|-------------|
| `--mcp-url` | Yes | — | Public ngrok URL of the running MCP server |
| `--query` | No | `"What is the capital of France?"` | Question to ask |
| `--model` | No | `claude-sonnet-4-20250514` | Anthropic model to use |

---

## test_mcp_bm25.py

Advanced test that uses a multi-hop, reasoning-intensive query to force multiple tool calls. Uses extended thinking.

### 1. Start the MCP server (separate terminal)

```bash
export JAVA_HOME=$(ls -d ~/amazon-corretto-*)
export PATH=$JAVA_HOME/bin:$PATH
source .venv/bin/activate
python searcher/mcp_server.py \
    --searcher-type bm25 \
    --index-path indexes/bm25 \
    --port 8080 \
    --public
```

### 2. Get the public URL

When the server starts it prints a line like:
```
Public MCP endpoint available at: https://xxxx.ngrok-free.app/mcp
```
Copy that URL and use it in the next step.

> **Note:** The ngrok URL is **not permanent** — it changes every time the server restarts (free tier).
> To get a stable URL, claim your free static domain at [dashboard.ngrok.com/domains](https://dashboard.ngrok.com/domains)
> and configure it in `~/.config/ngrok/ngrok.yml`.

### 3. Run the test

```bash
source .venv/bin/activate
ANTHROPIC_API_KEY=<your_key> python tests/test_mcp_bm25.py \
    --mcp-url "https://xxxx.ngrok-free.app/mcp"
```

**Arguments:**

| Argument | Required | Default | Description |
|----------|----------|---------|-------------|
| `--mcp-url` | Yes | — | Public ngrok URL of the running MCP server |
| `--model` | No | `claude-sonnet-4-20250514` | Anthropic model to use |
| `--budget` | No | `4096` | Thinking token budget |

---

## test_mcp_langchain.py

Simple LangChain + LangGraph ReAct agent that connects to the MCP server via `streamable-http` and uses the search tool to answer a query.

### 0. Install dependencies

```bash
conda activate wbr-mas
uv pip install langchain-mcp-adapters langchain-anthropic langgraph
```

### 1. Start the MCP server (separate terminal)

```bash
export JAVA_HOME=$(ls -d ~/amazon-corretto-*)
export PATH=$JAVA_HOME/bin:$PATH
source .venv/bin/activate
python searcher/mcp_server.py \
    --searcher-type bm25 \
    --index-path indexes/bm25 \
    --port 8080 \
    --public \
    --transport streamable-http
```

### 2. Get the public URL

When the server starts it prints a line like:
```
Public MCP endpoint available at: https://xxxx.ngrok-free.app/mcp
```
Copy that URL and use it in the next step.

### 3. Run the test

```bash
conda activate wbr-mas
ANTHROPIC_API_KEY=<your_key> python tests/test_mcp_langchain.py \
    --mcp-url "https://xxxx.ngrok-free.app/mcp" \
    --query "What is BM25?"
```

**Arguments:**

| Argument | Required | Default | Description |
|----------|----------|---------|-------------|
| `--mcp-url` | Yes | — | Public ngrok URL of the running MCP server |
| `--query` | No | `"What is BM25 retrieval?"` | Question to ask |
| `--model` | No | `claude-sonnet-4-6` | Anthropic model to use |

---

## Notes

- The ngrok URL is printed by the server on startup. Copy it before running the test.
- `ANTHROPIC_API_KEY` must be set as an environment variable.
- `test_mcp_bm25.py` and `test_mcp_langchain.py` require the BM25 index at `indexes/bm25/`. Download it first with:
  ```bash
  bash scripts_build_index/download_indexes.sh
  ```
