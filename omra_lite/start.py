#!/usr/bin/env python
"""
OMRA Lite Startup Script

This script initializes the database with example data and starts the backend.
"""
import os
import sys
import subprocess
import logging
import time
import asyncio
import signal
import webbrowser
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("omra_lite.start")

# Determine if we're running from a packaged executable
if getattr(sys, 'frozen', False):
    # Running as a bundled executable
    BASE_DIR = Path(sys._MEIPASS)
else:
    # Running as a regular Python script
    BASE_DIR = Path(__file__).parent

BACKEND_DIR = BASE_DIR / "backend"
FRONTEND_DIR = BASE_DIR / "frontend"

backend_process = None
frontend_process = None

def cleanup_processes(sig=None, frame=None):
    """Clean up processes on exit."""
    logger.info("Shutting down processes...")
    
    if backend_process:
        logger.info("Stopping backend process...")
        backend_process.terminate()
        try:
            backend_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            backend_process.kill()
    
    if frontend_process:
        logger.info("Stopping frontend process...")
        frontend_process.terminate()
        try:
            frontend_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            frontend_process.kill()
    
    logger.info("Shutdown complete!")
    sys.exit(0)

async def init_database():
    """Initialize the database."""
    logger.info("Initializing database...")
    
    # Check if MongoDB is running
    try:
        # Simple check to see if MongoDB is running
        import motor.motor_asyncio
        client = motor.motor_asyncio.AsyncIOMotorClient("mongodb://localhost:27017", serverSelectionTimeoutMS=5000)
        await client.admin.command('ping')
        logger.info("MongoDB is running")
    except Exception as e:
        logger.error(f"MongoDB is not running or not accessible: {e}")
        logger.error("Please make sure MongoDB is installed and running")
        sys.exit(1)
    
    # Run the database initialization script
    try:
        logger.info("Running database initialization script...")
        sys.path.append(str(BACKEND_DIR))
        from backend.init_db import init_db
        await init_db()
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        sys.exit(1)

def start_backend():
    """Start the backend server."""
    global backend_process
    
    logger.info("Starting backend server...")
    
    try:
        backend_process = subprocess.Popen(
            [sys.executable, "-m", "backend.main"],
            cwd=BASE_DIR,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            bufsize=1
        )
        
        # Wait for backend to start
        logger.info("Waiting for backend to start...")
        for i in range(30):  # Wait up to 30 seconds
            try:
                import httpx
                response = httpx.get("http://localhost:8000/health")
                if response.status_code == 200:
                    logger.info("Backend server is running")
                    return
            except Exception:
                time.sleep(1)
        
        logger.error("Backend server failed to start in time")
        cleanup_processes()
    except Exception as e:
        logger.error(f"Error starting backend: {e}")
        cleanup_processes()

def start_frontend():
    """Start the frontend server or open the static files."""
    global frontend_process
    
    # Check if we have a compiled frontend
    if os.path.exists(FRONTEND_DIR / "build" / "index.html"):
        logger.info("Using compiled frontend")
        # Open the UI in a browser
        webbrowser.open("http://localhost:8000")
        return
    
    # Otherwise, start the development server
    logger.info("Starting frontend development server...")
    
    try:
        # Check if npm is installed
        try:
            subprocess.run(["npm", "--version"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        except (subprocess.SubprocessError, FileNotFoundError):
            logger.error("npm is not installed or not in PATH")
            logger.error("Please install Node.js and npm to run the frontend development server")
            logger.info("Opening backend API documentation instead...")
            webbrowser.open("http://localhost:8000/docs")
            return
        
        # Check if dependencies are installed
        if not os.path.exists(FRONTEND_DIR / "node_modules"):
            logger.info("Installing frontend dependencies...")
            subprocess.run(["npm", "install"], cwd=FRONTEND_DIR, check=True)
        
        # Start the frontend development server
        frontend_process = subprocess.Popen(
            ["npm", "start"],
            cwd=FRONTEND_DIR,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            bufsize=1
        )
        
        # Wait for frontend to start
        logger.info("Waiting for frontend to start...")
        for i in range(30):  # Wait up to 30 seconds
            try:
                import httpx
                response = httpx.get("http://localhost:3000")
                if response.status_code == 200:
                    logger.info("Frontend server is running")
                    
                    # Open the UI in a browser
                    webbrowser.open("http://localhost:3000")
                    return
            except Exception:
                time.sleep(1)
        
        logger.warning("Frontend server failed to start in time")
        logger.info("Opening backend API documentation instead...")
        webbrowser.open("http://localhost:8000/docs")
    except Exception as e:
        logger.error(f"Error starting frontend: {e}")
        logger.info("Opening backend API documentation instead...")
        webbrowser.open("http://localhost:8000/docs")

def display_info():
    """Display information about the running application."""
    logger.info("OMRA Lite is running!")
    logger.info("Backend API: http://localhost:8000")
    logger.info("API Documentation: http://localhost:8000/docs")
    
    if os.path.exists(FRONTEND_DIR / "build" / "index.html"):
        # Using compiled frontend
        logger.info("Frontend: http://localhost:8000")
    else:
        # Using development server
        logger.info("Frontend (if running): http://localhost:3000")
    
    logger.info("Admin login credentials:")
    logger.info("  Username: admin")
    logger.info("  Password: admin1")
    logger.info("\nPress Ctrl+C to stop the application")

def monitor_processes():
    """Monitor the running processes and restart if needed."""
    global backend_process, frontend_process
    
    while True:
        # Check backend process
        if backend_process and backend_process.poll() is not None:
            logger.warning("Backend process has stopped. Restarting...")
            start_backend()
        
        # Check frontend process
        if frontend_process and frontend_process.poll() is not None:
            logger.warning("Frontend process has stopped. Restarting...")
            start_frontend()
        
        # Sleep for a bit
        time.sleep(5)

def main():
    """Main entry point."""
    # Set up signal handlers
    signal.signal(signal.SIGINT, cleanup_processes)
    signal.signal(signal.SIGTERM, cleanup_processes)
    
    try:
        # Initialize the database
        asyncio.run(init_database())
        
        # Start the backend
        start_backend()
        
        # Start the frontend
        start_frontend()
        
        # Display information
        display_info()
        
        # Monitor and keep the processes running
        monitor_processes()
    except KeyboardInterrupt:
        cleanup_processes()
    except Exception as e:
        logger.error(f"Error: {e}")
        cleanup_processes()

if __name__ == "__main__":
    main() 