#!/usr/bin/env python3
"""
Startup script for Social Media OCR Backend
"""

import uvicorn
import os
import sys
from pathlib import Path

# Add src to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from src.config.settings import get_settings

def main():
    """Main entry point"""
    settings = get_settings()
    
    print("🚀 Starting Social Media OCR Backend")
    print(f"📝 App: {settings.APP_NAME} v{settings.APP_VERSION}")
    print(f"🌍 Environment: {settings.ENVIRONMENT}")
    print(f"🔧 Debug: {settings.DEBUG}")
    print("-" * 50)
    
    # Run the server
    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level="info" if not settings.DEBUG else "debug"
    )

if __name__ == "__main__":
    main() 