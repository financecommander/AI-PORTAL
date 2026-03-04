# === CONSOLE INTELLIGENCE (Full Terminal Emulator) ===
specialists["console"] = {
    "name": "Console Intelligence",
    "model": "claude-3-5-sonnet-20241022",
    "tools": [SSHTerminalTool()],
    "description": "Advanced terminal emulator. Run commands on any VM safely. Type natural language like 'check ollama status on swarm-gpu'.",
    "system_prompt": "You are Console Intelligence — a powerful terminal assistant. Run real commands on the user's VMs. Be helpful, safe, and always ask for confirmation before running destructive commands."
}