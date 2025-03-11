"""
OMRA Lite Setup Diagnostic

This script checks for common issues when starting the backend server.
Run this script to diagnose problems with the backend setup.
"""
import os
import sys
import importlib
import socket
from pathlib import Path

def check_python_version():
    print(f"Python version: {sys.version}")
    if sys.version_info.major < 3 or (sys.version_info.major == 3 and sys.version_info.minor < 9):
        print("❌ Python 3.9+ is required")
        return False
    else:
        print("✅ Python version is compatible")
        return True

def check_directory_structure():
    backend_dir = Path(__file__).parent
    required_dirs = ["api"]
    required_files = [
        "main.py", 
        "db.py", 
        "models.py", 
        "agent_system.py",
        "api/__init__.py",
        "api/endpoints.py"
    ]
    
    print("\nChecking directory structure:")
    
    # Check required directories
    for dir_name in required_dirs:
        dir_path = backend_dir / dir_name
        if not dir_path.exists() or not dir_path.is_dir():
            print(f"❌ Missing directory: {dir_name}")
            if dir_name == "api":
                print("   Creating api directory...")
                dir_path.mkdir(exist_ok=True)
                (dir_path / "__init__.py").touch()
                print("   Created api directory and __init__.py file")
        else:
            print(f"✅ Directory exists: {dir_name}")
    
    # Check required files
    for file_name in required_files:
        file_path = backend_dir / file_name
        if not file_path.exists() or not file_path.is_file():
            print(f"❌ Missing file: {file_name}")
            if file_name == "api/__init__.py":
                api_init_path = backend_dir / "api" / "__init__.py"
                if not api_init_path.parent.exists():
                    api_init_path.parent.mkdir(exist_ok=True)
                api_init_path.touch()
                print("   Created api/__init__.py file")
        else:
            print(f"✅ File exists: {file_name}")

def check_mongodb():
    print("\nChecking MongoDB connection:")
    try:
        # Try to connect to MongoDB
        sock = socket.create_connection(("localhost", 27017), timeout=3)
        sock.close()
        print("✅ MongoDB is running")
        return True
    except (socket.timeout, ConnectionRefusedError):
        print("❌ MongoDB is not running")
        return False

def check_dependencies():
    print("\nChecking dependencies:")
    required_packages = [
        "fastapi", 
        "uvicorn", 
        "pydantic", 
        "motor", 
        "pymongo",
        "python-jose",
        "passlib",
        "httpx"
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            importlib.import_module(package)
            print(f"✅ {package} is installed")
        except ImportError:
            print(f"❌ {package} is missing")
            missing_packages.append(package)
    
    if missing_packages:
        print("\nInstall missing packages with:")
        print(f"pip install {' '.join(missing_packages)}")

def create_api_init():
    """Create a simple __init__.py file for the API package."""
    backend_dir = Path(__file__).parent
    api_dir = backend_dir / "api"
    
    if not api_dir.exists():
        api_dir.mkdir(exist_ok=True)
        print("Created api directory")
    
    init_file = api_dir / "__init__.py"
    
    if not init_file.exists():
        with open(init_file, "w") as f:
            f.write('"""API package for OMRA Lite."""\n\nfrom fastapi import APIRouter\n\napi_router = APIRouter()\n')
        print("Created api/__init__.py file")

def check_endpoints_file():
    """Check if endpoints.py exists and create a simple one if not."""
    backend_dir = Path(__file__).parent
    endpoints_file = backend_dir / "api" / "endpoints.py"
    
    if not endpoints_file.exists():
        with open(endpoints_file, "w") as f:
            f.write('"""API endpoints for OMRA Lite."""\n\nfrom fastapi import APIRouter, Depends, HTTPException, status\nfrom datetime import datetime\n\nfrom api import api_router\nfrom models import User\nfrom db import get_database\n\n@api_router.get("/health")\nasync def health_check():\n    """Health check endpoint."""\n    return {"status": "ok"}\n')
        print("Created api/endpoints.py file with health check endpoint")
        return False
    return True

def check_import_issues():
    """Try importing key modules to catch import errors."""
    print("\nChecking module imports:")
    modules_to_check = [
        "models", 
        "db", 
        "agent_system",
        "api"
    ]
    
    sys.path.append(str(Path(__file__).parent.parent))
    
    for module in modules_to_check:
        try:
            importlib.import_module(f"backend.{module}")
            print(f"✅ Successfully imported {module}")
        except ImportError as e:
            print(f"❌ Error importing {module}: {str(e)}")

def main():
    print("=" * 50)
    print("OMRA Lite Setup Diagnostics")
    print("=" * 50)
    
    check_python_version()
    check_directory_structure()
    check_mongodb()
    check_dependencies()
    
    # Create API init file if missing
    create_api_init()
    
    # Check endpoints file
    check_endpoints_file()
    
    # Check for import issues
    check_import_issues()
    
    print("\nDiagnostics complete!")
    print("\nTo manually start the backend server:")
    print("1. Open a terminal in the backend directory")
    print("2. Run: python main.py")
    print("\nOnce the server is running, access the API docs at:")
    print("http://localhost:8000/docs")
    print("\nLogin with:")
    print("Username: admin")
    print("Password: admin1")

if __name__ == "__main__":
    main() 