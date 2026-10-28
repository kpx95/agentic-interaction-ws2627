"""Entry point for the Exercise 1 agent."""

from agent.config import load_config


def main() -> None:
    load_config()
    print("Configuration loaded. Agent behavior will be added in the next step.")


if __name__ == "__main__":
    main()
