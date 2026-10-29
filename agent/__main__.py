"""Command-line entry point for the calendar question-answering agent."""

from __future__ import annotations

from datetime import datetime, timezone
import json
import sys
import time
from typing import Any
import uuid

from openai import OpenAI

from agent.config import REPOSITORY_ROOT, load_config
from agent.tools import TOOL_DEFINITION, get_calendar_day


class RunLog:
    """Write one JSONL file containing the events from a single run."""

    def __init__(self, model: str | None) -> None:
        self.run_id = str(uuid.uuid4())
        self.model = model
        log_dir = REPOSITORY_ROOT / "logs"
        log_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
        self.path = log_dir / f"{timestamp}-{self.run_id}.jsonl"

    def write(
        self,
        event: str,
        *,
        ok: bool,
        duration_ms: int = 0,
        tool: str | None = None,
        args: Any = None,
    ) -> None:
        record = {
            "ts": datetime.now(timezone.utc).isoformat(),
            "run_id": self.run_id,
            "event": event,
            "tool": tool,
            "args": args,
            "ok": ok,
            "model": self.model,
            "duration_ms": duration_ms,
        }
        with self.path.open("a", encoding="utf-8") as log_file:
            log_file.write(json.dumps(record, ensure_ascii=False) + "\n")


def _call_calendar_tool(name: str, raw_arguments: str, data_base_url: str) -> dict[str, Any]:
    if name != "get_calendar_day":
        raise ValueError(f"The model requested an unknown tool: {name}")
    arguments = json.loads(raw_arguments)
    if not isinstance(arguments, dict) or set(arguments) != {"date"}:
        raise ValueError("get_calendar_day expects exactly one 'date' argument")
    return get_calendar_day(arguments["date"], data_base_url)


def answer_question(task: str, run_log: RunLog) -> str:
    """Ask the configured model, execute its calendar call, and return its answer."""
    config = load_config()
    run_log.model = config.model
    client = OpenAI(
        api_key=config.openai_api_key,
        base_url=config.openai_base_url,
    )
    messages: list[dict[str, Any]] = [
        {
            "role": "system",
            "content": (
                "You answer questions about a calendar. Always use the "
                "get_calendar_day tool to look up the relevant date before "
                "answering. Convert dates from the user's language to "
                "YYYY-MM-DD. Treat a no_data result as meaning no calendar "
                "entries are available for that date. Answer in the user's "
                "language, using only the returned calendar data."
            ),
        },
        {"role": "user", "content": task},
    ]

    started = time.perf_counter()
    first_response = client.chat.completions.create(
        model=config.model,
        messages=messages,
        tools=[TOOL_DEFINITION],
        tool_choice="required",
    )
    first_duration = round((time.perf_counter() - started) * 1000)
    assistant_message = first_response.choices[0].message
    tool_calls = assistant_message.tool_calls or []
    if not tool_calls:
        raise RuntimeError("The model returned no calendar tool call")

    messages.append(assistant_message.model_dump(exclude_none=True))
    for tool_call in tool_calls:
        name = tool_call.function.name
        raw_arguments = tool_call.function.arguments
        try:
            parsed_arguments = json.loads(raw_arguments)
        except json.JSONDecodeError:
            parsed_arguments = {"raw": raw_arguments}

        run_log.write(
            "tool_call",
            ok=True,
            duration_ms=first_duration,
            tool=name,
            args={"call_id": tool_call.id, "arguments": parsed_arguments},
        )

        started = time.perf_counter()
        try:
            result = _call_calendar_tool(name, raw_arguments, config.data_base_url)
        except Exception as exc:
            duration = round((time.perf_counter() - started) * 1000)
            run_log.write(
                "tool_result",
                ok=False,
                duration_ms=duration,
                tool=name,
                args={"call_id": tool_call.id, "arguments": parsed_arguments, "error": str(exc)},
            )
            raise

        duration = round((time.perf_counter() - started) * 1000)
        run_log.write(
            "tool_result",
            ok=True,
            duration_ms=duration,
            tool=name,
            args={"call_id": tool_call.id, "arguments": parsed_arguments, "result": result},
        )
        messages.append(
            {
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": json.dumps(result, ensure_ascii=False),
            }
        )

    started = time.perf_counter()
    final_response = client.chat.completions.create(
        model=config.model,
        messages=messages,
    )
    duration = round((time.perf_counter() - started) * 1000)
    answer = final_response.choices[0].message.content
    if not answer or not answer.strip():
        raise RuntimeError("The model returned an empty answer")

    answer = answer.strip()
    run_log.write(
        "final",
        ok=True,
        duration_ms=duration,
        tool="chat.completions.create",
        args={"answer": answer},
    )
    return answer


def main() -> int:
    task = " ".join(sys.argv[1:]).strip()
    run_log = RunLog(model=None)
    run_log.write("user_task", ok=bool(task), args={"task": task})

    if not task:
        message = 'Usage: python -m agent "Your calendar question"'
        run_log.write("error", ok=False, args={"message": message})
        print(message, file=sys.stderr)
        return 2

    try:
        answer = answer_question(task, run_log)
    except Exception as exc:
        run_log.write("error", ok=False, args={"message": str(exc)})
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    print(answer)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
