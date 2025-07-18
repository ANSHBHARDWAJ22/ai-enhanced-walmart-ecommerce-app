#!/usr/bin/env python3
"""
Production runner for Walmart Clone Flask Application
"""

from app import app
import os

if __name__ == '__main__':
    # Get port from environment variable or default to 5000
    port = int(os.environ.get('PORT', 5000))
    
    # Get debug mode from environment
    debug = os.environ.get('FLASK_ENV') == 'development'
    
    # Run the application
    app.run(
        host='0.0.0.0',
        port=port,
        debug=debug
    )