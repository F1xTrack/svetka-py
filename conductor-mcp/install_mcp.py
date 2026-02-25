import json
import os
from pathlib import Path

config_path = Path.home() / ".config" / "opencode" / "opencode.json"

if not config_path.exists():
    print(f"Error: Config not found at {config_path}")
    exit(1)

with open(config_path, "r", encoding="utf-8") as f:
    config = json.load(f)

if "mcp" not in config:
    config["mcp"] = {}

# Добавляем или обновляем запись о conductor
config["mcp"]["conductor"] = {
    "type": "local",
    "command": ["python", "G:\_Projects\svetka_py\conductor-mcp\server.py"]
}

with open(config_path, "w", encoding="utf-8") as f:
    json.dump(config, f, indent=2)

print("Successfully added Conductor MCP to opencode config.")
