# Test Scripts Guide

This document explains how to run the two MCP test scripts: `test_mcp_faiss.py` and `test_mcp_bm25.py`.

## Prerequisites

Activate the virtual environment:
```bash
source .venv/bin/activate
```

If using BM25 (required for `test_mcp_bm25.py`), Java 21 must be installed. The recommended way without sudo is via conda:

```bash
conda install -c conda-forge openjdk=21
```

Then set `JAVA_HOME`:
```bash
export JAVA_HOME=$(ls -d ~/amazon-corretto-*)   # adjust to your Java install path
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

### 2. Run the test

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

### 2. Run the test

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

## Notes

- The ngrok URL is printed by the server on startup. Copy it before running the test.
- `ANTHROPIC_API_KEY` must be set as an environment variable.
- `test_mcp_bm25.py` requires the BM25 index at `indexes/bm25/`. Download it first with:
  ```bash
  bash scripts_build_index/download_indexes.sh
  ```
