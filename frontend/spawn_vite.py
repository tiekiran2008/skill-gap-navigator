import os
import sys
import subprocess

pid = os.spawnl(
    os.P_NOWAIT,
    sys.executable,
    sys.executable,
    '-c',
    'import subprocess; subprocess.Popen([r"D:\\tool\\nodejs\\node-v24.18.0-win-x64\\node.exe", "node_modules/vite/bin/vite.js", "--port", "5173"], cwd=r"D:\\KAI-LLM\\java project\\frontend", stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)'
)
print(f"Vite PID: {pid}")
