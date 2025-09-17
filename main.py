from __future__ import annotations
from fastapi import FastAPI
from routes import router
import os
import uvicorn

def create_app() -> FastAPI:
    app = FastAPI(title="Sprouts Chat API")
    app.include_router(router)
    return app

app = create_app()

if __name__ == "__main__":
    host = os.getenv("HOST", "0.0.0.0")
    port_str = os.getenv("PORT", "8000")
    reload_env = os.getenv("RELOAD", "false").lower()
    reload = reload_env in ("1", "true", "yes", "on")

    uvicorn.run(app, host=host, port=int(port_str), reload=reload)

