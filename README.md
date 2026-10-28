# Agentic Human-AI Interaction — Exercise 1

This repository contains the work for Exercise 1, “First Tool Call”.

## Setup

Use Python 3.11 or newer. From the repository root, create and activate a virtual environment, then install the dependencies:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Copy `.env.example` to `.env` and add your model provider API key to `OPENAI_API_KEY`. Keep `.env` local; it is ignored by Git. Do not put API keys in commits or chat messages. Values already set in the process environment take precedence over values in `.env`.

The default endpoint and model use Groq's OpenAI-compatible Chat Completions API. Calendar data is queried over HTTP from `DATA_BASE_URL`; the data repository is read-only and its contents must not be copied into this repository.

## Calendar tool

The `get_calendar_day` tool in `agent/tools.py` accepts a date in `YYYY-MM-DD` format and reads that day's appointments from `{DATA_BASE_URL}/calendar/{date}.json`. A 404 is returned as a `no_data` result rather than an exception. The tool's function name, description, and parameter schema are defined in `TOOL_DEFINITION`.

The agent will be run from the repository root with:

```bash
python -m agent "Your calendar question"
```
