from fastapi import FastAPI
from typing import Dict, Any


class BaseMCPServer:
    """Base class for MCP servers."""

    def __init__(self, server_name: str, port: int):
        self.server_name = server_name
        self.port = port
        self.app = FastAPI(title=f"{server_name} MCP Server", version="1.0.0")
        self._setup_routes()

    def _setup_routes(self):
        @self.app.get("/health")
        async def health():
            return {
                "status": "healthy",
                "server": self.server_name,
                "port": self.port,
            }

        @self.app.get("/info")
        async def info():
            return {
                "name": self.server_name,
                "version": "1.0.0",
                "type": "MCP Server",
            }

    def run(self):
        import uvicorn

        uvicorn.run(
            self.app,
            host="0.0.0.0",
            port=self.port,
            log_level="info",
        )
