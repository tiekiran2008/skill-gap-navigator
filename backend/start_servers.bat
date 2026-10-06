@echo off
cd /d "D:\KAI-LLM\java project\backend"
start "" /B "C:\Users\kelum\AppData\Local\Programs\Python\Python311\python.exe" -m uvicorn app.main:app --host 0.0.0.0 --port 8000
cd /d "D:\KAI-LLM\java project\frontend"
start "" /B "C:\Users\kelum\AppData\Local\Programs\Python\Python311\python.exe" serve_dist.py
echo Servers started
