@echo off
cd /d "D:\KAI-LLM\java project\backend"
"C:\Users\kelum\AppData\Local\Programs\Python\Python311\python.exe" -m uvicorn app.main:app --host 0.0.0.0 --port 8000
