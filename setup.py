#!/usr/bin/env python3
"""
Setup script for Celiac Nutrition Hub
"""

import os
import sys
import subprocess
import sqlite3
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        sys.exit(1)
    print("✅ Python version is compatible")

def install_dependencies():
    """Install required dependencies"""
    print("📦 Installing dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed successfully")
    except subprocess.CalledProcessError:
        print("❌ Failed to install dependencies")
        sys.exit(1)

def create_env_file():
    """Create .env file if it doesn't exist"""
    env_file = Path(".env")
    if not env_file.exists():
        print("🔧 Creating .env file...")
        env_content = """# Celiac Nutrition Hub Environment Variables
# Get your Spoonacular API key from https://spoonacular.com/food-api
SPOONACULAR_API_KEY=your_api_key_here

# Secret key for session management
SECRET_KEY=your_secret_key_here

# Application settings
DEBUG=True
LOG_LEVEL=INFO
SESSION_TIMEOUT=1800
"""
        with open(env_file, "w") as f:
            f.write(env_content)
        print("✅ .env file created")
        print("⚠️  Please update the .env file with your actual API keys")
    else:
        print("✅ .env file already exists")

def initialize_database():
    """Initialize the database"""
    print("🗄️  Initializing database...")
    try:
        # Import the main app to run database initialization
        import celiac_nutrition_app
        print("✅ Database initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize database: {e}")
        sys.exit(1)

def create_directories():
    """Create necessary directories"""
    print("📁 Creating directories...")
    directories = ["logs", "backups", "uploads"]
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
    print("✅ Directories created")

def main():
    """Main setup function"""
    print("🌾 Setting up Celiac Nutrition Hub...")
    print("=" * 50)
    
    # Check Python version
    check_python_version()
    
    # Install dependencies
    install_dependencies()
    
    # Create environment file
    create_env_file()
    
    # Create directories
    create_directories()
    
    # Initialize database
    initialize_database()
    
    print("=" * 50)
    print("🎉 Setup completed successfully!")
    print("\nNext steps:")
    print("1. Update the .env file with your Spoonacular API key")
    print("2. Run the application: streamlit run celiac_nutrition_app.py")
    print("3. Open your browser to http://localhost:8501")
    print("\nFor more information, see the README.md file")

if __name__ == "__main__":
    main()