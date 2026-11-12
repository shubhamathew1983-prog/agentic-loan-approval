#!/usr/bin/env python
"""Start all MCP servers."""

import asyncio
import threading
from app.mcp_servers import (
    ApplicantDBMCP,
    RiskRulesDBMCP,
    NotificationSystemMCP,
)
from app.utils import get_logger

logger = get_logger(__name__)


def run_server(mcp_server_class, port):
    """Run a single MCP server in a thread."""
    try:
        server = mcp_server_class(port)
        logger.info(f"Starting {server.server_name} on port {port}")
        server.run()
    except Exception as e:
        logger.error(f"Error running MCP server on port {port}: {str(e)}")


def main():
    """Run all MCP servers."""
    print("🚀 Starting MCP Servers...")
    print("")

    # Define MCP servers
    servers = [
        (ApplicantDBMCP, 8001),
        (RiskRulesDBMCP, 8002),
        (NotificationSystemMCP, 8003),
    ]

    # Start each server in a separate thread
    threads = []
    for server_class, port in servers:
        thread = threading.Thread(
            target=run_server,
            args=(server_class, port),
            daemon=True,
        )
        thread.start()
        threads.append(thread)
        print(f"✓ {server_class.__name__} starting on port {port}")

    print("")
    print("✅ All MCP servers started!")
    print("")
    print("Available MCP Servers:")
    for server_class, port in servers:
        print(f"  - {server_class.__name__:20} http://localhost:{port}")
    print("")

    # Keep main thread alive
    try:
        for thread in threads:
            thread.join()
    except KeyboardInterrupt:
        print("\nShutting down MCP servers...")


if __name__ == "__main__":
    main()
