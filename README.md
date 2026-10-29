# Agentic Human-AI Interaction — Exercise 1

This repository contains the work for Exercise 1, “First Tool Call”.

## Setup

Use Python 3.11 or newer. From the repository root, create and activate a virtual environment, then install the dependencies:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Create a local `.env` file in the repository root with these settings, then add your model provider API key to `OPENAI_API_KEY`:

```dotenv
OPENAI_BASE_URL=https://api.groq.com/openai/v1
MODEL=openai/gpt-oss-20b
OPENAI_API_KEY=your-api-key
DATA_BASE_URL=https://jhbelz.github.io/agentic-interaction-data/v1
```

Keep `.env` local; it is ignored by Git. Do not put API keys in commits or chat messages. Values already set in the process environment take precedence over values in `.env`.

The example endpoint and model use Groq's OpenAI-compatible Chat Completions API. Calendar data is queried over HTTP from `DATA_BASE_URL`; the data repository is read-only and its contents must not be copied into this repository.

## Calendar tool

The `get_calendar_day` tool in `agent/tools.py` accepts a date in `YYYY-MM-DD` format and reads that day's appointments from `{DATA_BASE_URL}/calendar/{date}.json`. A 404 is returned as a `no_data` result rather than an exception. The tool's function name, description, and parameter schema are defined in `TOOL_DEFINITION`.

The agent will be run from the repository root with:

```bash
python -m agent "Your calendar question"
```

For example:

```bash
python -m agent "Was steht am 29.10.2026 im Kalender?"
```

The agent requires the model to call the calendar tool, sends the tool result
back to the model, and prints the final answer to standard output. Each run
writes a JSONL log with a unique run ID under `logs/`; logs are ignored by Git.
