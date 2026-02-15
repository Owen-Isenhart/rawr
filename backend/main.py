"""
Entry point for development. In production, use: uvicorn app.main:app --host 0.0.0.0 --port 8000
"""
import os
import uvicorn

if __name__ == "__main__":
    # Read config from environment
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    reload = os.getenv("ENV", "development") != "production"
    
    print(f"Starting AI Battle Arena on {host}:{port} (reload={reload})")
    
    uvicorn.run(
        "app.main:app",
        host=host,
        port=port,
        reload=reload,
        log_level="info"
    )

