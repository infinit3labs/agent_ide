"""Demo script for the config-driven agent application."""

from agent_ide import AgentApp


def main() -> None:
    app = AgentApp.from_file("config.yaml")
    result = app.run()
    print(result)


if __name__ == "__main__":
    main()
