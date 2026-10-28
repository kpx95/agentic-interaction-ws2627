# Agentic Human-AI Interaction — Exercise 1

This repository contains the work for Exercise 1, “First Tool Call”.

## Setup

Use Python 3.11 or newer. From the repository root, create and activate a virtual environment, then install the dependencies:

```bash
python -m venv .venv
.venv\Scripts\Activate.ps1  # Windows PowerShell
pip install -r requirements.txt
```

Copy `.env.example` to `.env` and add your model provider API key to `OPENAI_API_KEY`. Keep `.env` local; it is ignored by Git. Do not put API keys in commits or chat messages. Values already set in the process environment take precedence over values in `.env`.

The default endpoint and model use Groq's OpenAI-compatible Chat Completions API. The agent will read the calendar data from `DATA_BASE_URL` over HTTP. The mock data repository is read-only; do not copy its data into this repository.

The agent will be run from the repository root with:

```bash
python -m agent "Your calendar question"
```
