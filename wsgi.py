"""
ResumeIQ v2 — WSGI/ASGI Entry Point
Use: uvicorn wsgi:app --host 0.0.0.0 --port 8000
"""
from backend.main import app

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("wsgi:app", host="0.0.0.0", port=8000, reload=True)
