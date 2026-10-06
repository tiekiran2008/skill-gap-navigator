import subprocess, sys, os, time, socket

# Start Vite detached
p = subprocess.Popen(
    [sys.executable, '-c', 'import subprocess; subprocess.Popen([r"D:\\tool\\nodejs\\node-v24.18.0-win-x64\\node.exe", "node_modules/vite/bin/vite.js", "--port", "5173"], cwd=r"D:\\KAI-LLM\\java project\\frontend", stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)'],
    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
)
print("Launcher started")
time.sleep(3)
s = socket.socket()
print('5173:', 'OPEN' if s.connect_ex(('127.0.0.1',5173))==0 else 'CLOSED')
s.close()
