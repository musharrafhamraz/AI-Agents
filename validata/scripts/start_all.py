"""Start all Validata services"""
import subprocess
import sys
import time
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))


def start_service(name, command, cwd=None):
    """Start a service in a new process"""
    print(f"Starting {name}...")
    try:
        process = subprocess.Popen(
            command,
            shell=True,
            cwd=cwd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        time.sleep(2)  # Give it time to start
        
        if process.poll() is None:
            print(f"✓ {name} started (PID: {process.pid})")
            return process
        else:
            print(f"✗ {name} failed to start")
            return None
    except Exception as e:
        print(f"✗ Error starting {name}: {e}")
        return None


def main():
    """Main startup function"""
    print("=" * 60)
    print("Validata Platform - Starting All Services")
    print("=" * 60)
    print()
    
    processes = []
    
    # Start MCP Servers
    print("Starting MCP Servers...")
    print("-" * 60)
    
    mcp_servers = [
        ("Memory MCP Server", "python mcp_servers/memory/server.py"),
        ("Survey MCP Server", "python mcp_servers/survey/server.py"),
        ("Validation MCP Server", "python mcp_servers/validation/server.py"),
        ("Analytics MCP Server", "python mcp_servers/analytics/server.py"),
    ]
    
    for name, command in mcp_servers:
        process = start_service(name, command)
        if process:
            processes.append((name, process))
    
    print()
    
    # Start FastAPI Backend
    print("Starting FastAPI Backend...")
    print("-" * 60)
    backend_process = start_service(
        "FastAPI Backend",
        "uvicorn backend.api.main:app --reload --host 0.0.0.0 --port 8000"
    )
    if backend_process:
        processes.append(("FastAPI Backend", backend_process))
    
    print()
    
    # Start Next.js Frontend
    print("Starting Next.js Frontend...")
    print("-" * 60)
    frontend_process = start_service(
        "Next.js Frontend",
        "npm run dev",
        cwd="frontend"
    )
    if frontend_process:
        processes.append(("Next.js Frontend", frontend_process))
    
    print()
    print("=" * 60)
    print("✓ All services started!")
    print("=" * 60)
    print()
    print("Access points:")
    print("  - Frontend:  http://localhost:3000")
    print("  - Backend:   http://localhost:8000")
    print("  - API Docs:  http://localhost:8000/docs")
    print()
    print("MCP Servers:")
    print("  - Memory:     http://localhost:5002")
    print("  - Survey:     http://localhost:5001")
    print("  - Validation: http://localhost:5003")
    print("  - Analytics:  http://localhost:5004")
    print()
    print("Press Ctrl+C to stop all services")
    print()
    
    try:
        # Keep script running
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\nStopping all services...")
        for name, process in processes:
            print(f"Stopping {name}...")
            process.terminate()
            process.wait()
        print("\n✓ All services stopped")


if __name__ == "__main__":
    main()
