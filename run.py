#!/usr/bin/env python
"""
BirdQuest - Run Script
Easy startup script for the BirdQuest application.
"""

import os
import sys


def main():
    """Initialize and run the BirdQuest application."""
    # Ensure we're in the correct directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)

    # Add the script directory to the Python path
    if script_dir not in sys.path:
        sys.path.insert(0, script_dir)

    # Import the app
    from app import app, db, init_db

    # Initialize the database
    print("🐦 Initializing BirdQuest...")
    init_db()
    print("✅ Database initialized!")

    # Configuration
    host = os.environ.get("FLASK_HOST", "127.0.0.1")
    port = int(os.environ.get("FLASK_PORT", 5000))
    debug = os.environ.get("FLASK_DEBUG", "1") == "1"

    # Run the application
    print(f"\n🚀 Starting BirdQuest on http://{host}:{port}")
    print("📝 Press CTRL+C to stop the server\n")

    try:
        app.run(host=host, port=port, debug=debug)
    except KeyboardInterrupt:
        print("\n\n👋 BirdQuest stopped. See you next time!")
        sys.exit(0)


if __name__ == "__main__":
    main()
