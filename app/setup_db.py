#!/usr/bin/env python3
"""
Database setup script for AsyncJobQueue.
This script creates the database tables and can be used for initial setup.
"""

import asyncio
import os
import sys

# Add the app directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.db import init_db
from app.config import DB_URL

async def setup_database():
    """Initialize the database tables."""
    print("Setting up database...")
    print(f"Database URL: {DB_URL}")
    
    try:
        await init_db()
        print("✅ Database tables created successfully!")
        print("\nTables created:")
        print("- jobs (stores job information, status, and results)")
        print("\nYou can now start the FastAPI application.")
        
    except Exception as e:
        print(f"❌ Error setting up database: {e}")
        print("\nMake sure:")
        print("1. PostgreSQL is running")
        print("2. Database 'asyncjobqueue' exists")
        print("3. User has proper permissions")
        print("4. Connection details in config.py are correct")

if __name__ == "__main__":
    asyncio.run(setup_database()) 