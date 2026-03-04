from crewai.tools import BaseTool
from pydantic import BaseModel, Field
import paramiko

class SSHCommandInput(BaseModel):
    vm_name: str = Field(..., description="Which VM? (fc-ai-portal, swarm-gpu, swarm-mainframe, calculus-web)")
    command: str = Field(..., description="The shell command to run (or natural language)")

class SSHTerminalTool(BaseTool):
    name: str = "ssh_terminal"
    description: str = "Run shell commands on any of your VMs securely. You can use natural language like 'check ollama status on swarm-gpu'."
    args_schema = SSHCommandInput

    def _run(self, vm_name: str, command: str) -> str:
        vm_map = {
            "fc-ai-portal": "34.75.120.202",
            "swarm-gpu": "34.73.21.223",
            "swarm-mainframe": "34.74.80.83",
            "calculus-web": "34.139.78.75"
        }
        host = vm_map.get(vm_name.lower(), vm_name)

        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(host, username="crypticassassin", timeout=15)
            stdin, stdout, stderr = ssh.exec_command(command)
            output = stdout.read().decode() + stderr.read().decode()
            ssh.close()
            return output.strip() or "✅ Command executed successfully (no output)"
        except Exception as e:
            return f"❌ Error connecting to {vm_name} ({host}): {str(e)}"
