#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os

# Print system info
print(f"Python version: {sys.version}")
print(f"Python executable: {sys.executable}")
print(f"Current working directory: {os.getcwd()}")
print(f"Python path: {sys.path}")

# Check venv site-packages
venv_site_packages = os.path.join(os.getcwd(), "venv", "lib", "python3.13", "site-packages")
print(f"Checking if venv site-packages exists: {os.path.exists(venv_site_packages)}")
if os.path.exists(venv_site_packages):
    print(f"Venv site-packages directory contents:")
    for item in sorted(os.listdir(venv_site_packages)):
        print(f"  - {item}")
    
    # Add site-packages to path
    if venv_site_packages not in sys.path:
        print(f"Adding {venv_site_packages} to Python path")
        sys.path.insert(0, venv_site_packages)

# Add the project root to the Python path
project_root = os.getcwd()
if project_root not in sys.path:
    print(f"Adding {project_root} to Python path")
    sys.path.insert(0, project_root)

# Try imports after path adjustments
print("\nTrying imports after path adjustments:")
try:
    from sqlmodel import SQLModel
    print("Successfully imported SQLModel")
except ImportError as e:
    print(f"Failed to import SQLModel: {e}")

try:
    from app.database import engine, get_session
    print("Successfully imported database module")
except ImportError as e:
    print(f"Failed to import database module: {e}")

try:
    from app.models.user_model import User
    print("Successfully imported User model")
except ImportError as e:
    print(f"Failed to import User model: {e}")

try:
    from app.models.post_model import Post
    print("Successfully imported Post model")
except ImportError as e:
    print(f"Failed to import Post model: {e}") 