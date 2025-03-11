#!/usr/bin/env python
"""
OMRA Lite Run Script

This script helps set up and run the OMRA Lite application.
It checks for MongoDB, starts the backend server, and opens the browser.
"""
import os
import sys
import subprocess
import time
import webbrowser
import platform
import socket
from pathlib import Path

def check_mongodb_running():
    """Check if MongoDB is running."""
    try:
        # Try to connect to MongoDB
        sock = socket.create_connection(("localhost", 27017), timeout=3)
        sock.close()
        print("✅ MongoDB is running")
        return True
    except (socket.timeout, ConnectionRefusedError):
        print("❌ MongoDB is not running")
        return False

def suggest_mongodb_installation():
    """Suggest MongoDB installation based on OS."""
    system = platform.system()
    
    print("\nYou need to install and start MongoDB first:")
    
    if system == "Windows":
        print("\nWindows Installation:")
        print("1. Download MongoDB Community Server from https://www.mongodb.com/try/download/community")
        print("2. Run the installer and follow the instructions")
        print("3. Start MongoDB service from Services or run 'net start MongoDB' as administrator")
    
    elif system == "Darwin":  # macOS
        print("\nmacOS Installation:")
        print("1. Install Homebrew if not already installed (https://brew.sh/)")
        print("2. Run: brew tap mongodb/brew")
        print("3. Run: brew install mongodb-community")
        print("4. Start MongoDB: brew services start mongodb-community")
    
    else:  # Linux
        print("\nLinux Installation:")
        print("1. Follow the installation guide for your distribution: https://docs.mongodb.com/manual/administration/install-on-linux/")
        print("2. Start MongoDB: sudo systemctl start mongod")
    
    print("\nAfter installing and starting MongoDB, run this script again.")

def start_backend_server():
    """Start the backend server."""
    print("Starting backend server...")
    backend_dir = Path(__file__).parent / "backend"
    
    if platform.system() == "Windows":
        subprocess.Popen(["start", "cmd", "/k", sys.executable, "main.py"], cwd=backend_dir, shell=True)
    else:
        # For macOS and Linux
        subprocess.Popen(["python", "main.py"], cwd=backend_dir)
    
    print("Backend server starting... please wait")
    
    # Wait for the server to start
    for _ in range(30):  # Wait up to 30 seconds
        try:
            resp = requests.get("http://localhost:8000/health")
            if resp.status_code == 200:
                print("✅ Backend server is running")
                return True
        except Exception:
            time.sleep(1)
    
    print("❌ Failed to start backend server")
    return False

def open_browser():
    """Open the browser to the application URL."""
    url = "http://localhost:8000/docs"
    print(f"Opening {url} in your browser")
    webbrowser.open(url)
    
    print("\nLogin credentials:")
    print("  Username: admin")
    print("  Password: admin1")

def main():
    """Main function."""
    print("=" * 50)
    print("OMRA Lite Setup")
    print("=" * 50)
    
    # Check if MongoDB is running
    if not check_mongodb_running():
        suggest_mongodb_installation()
        return
    
    # Start the backend server
    if start_backend_server():
        time.sleep(2)
        open_browser()
        
        print("\nSetup complete! You can now use OMRA Lite.")
        print("\nTo add API keys to the system:")
        print("1. Login with the credentials above")
        print("2. Go to Settings in the sidebar")
        print("3. Click 'Add API Key'")
        print("4. Select the key type (e.g., ANTHROPIC_API_KEY) and enter your key")
        
        print("\nPress Ctrl+C to exit")
        
        try:
            # Keep the script running
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nExiting OMRA Lite...")
    else:
        print("Failed to set up OMRA Lite. Please check the logs for errors.")

if __name__ == "__main__":
    try:
        import requests
    except ImportError:
        print("Installing requirements...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "requests"])
        import requests
    
    main() 