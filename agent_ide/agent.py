"""Core application logic."""

from .config import AppConfig, load_config
from . import operations

OPERATION_MAP = {
    "uppercase": operations.uppercase,
    "prefix": operations.prefix,
}


class AgentApp:
    """Execute a series of operations defined in configuration."""

    def __init__(self, config: AppConfig):
        self.config = config

    @classmethod
    def from_file(cls, path: str) -> "AgentApp":
        return cls(load_config(path))

    def run(self) -> str:
        text = self.config.input_text
        for op in self.config.operations:
            func = OPERATION_MAP.get(op.type)
            if func is None:
                raise ValueError(f"Unknown operation: {op.type}")
            text = func(text, **op.params)
        return text
