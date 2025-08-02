from agent_ide import AgentApp


def test_pipeline(tmp_path):
    cfg = tmp_path / "config.yaml"
    cfg.write_text(
        "input_text: hi\n"
        "operations:\n"
        "  - type: uppercase\n"
        "  - type: prefix\n"
        "    value: 'Agent: '\n"
    )
    app = AgentApp.from_file(str(cfg))
    assert app.run() == "Agent: HI"
