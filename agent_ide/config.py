from dataclasses import dataclass
from typing import Any, Dict, List
import yaml


@dataclass
class OperationConfig:
    """Configuration for a single operation."""
    type: str
    params: Dict[str, Any]


@dataclass
class AppConfig:
    """Application configuration."""
    input_text: str
    operations: List[OperationConfig]


def load_config(path: str) -> AppConfig:
    """Load configuration from a YAML file."""
    with open(path, "r", encoding="utf-8") as fh:
        raw = yaml.safe_load(fh) or {}
    ops = [
        OperationConfig(
            type=op.get("type", ""),
            params={k: v for k, v in op.items() if k != "type"},
        )
        for op in raw.get("operations", [])
    ]
    return AppConfig(input_text=raw.get("input_text", ""), operations=ops)
