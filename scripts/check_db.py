#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys

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

from sqlmodel import Session, select, func
from app.database import engine
from app.models.user_model import User
from app.models.post_model import Post

def main():
    with Session(engine) as session:
        # Count users
        user_count = session.exec(select(func.count()).select_from(User)).one()
        print(f"Total users: {user_count}")
        
        # Count posts
        post_count = session.exec(select(func.count()).select_from(Post)).one()
        print(f"Total posts: {post_count}")
        
        # Sample users
        users = session.exec(select(User).limit(3)).all()
        print("\nSample users:")
        for user in users:
            print(f"- {user.username} ({user.email})")
        
        # Sample posts
        posts = session.exec(select(Post).limit(3)).all()
        print("\nSample posts:")
        for post in posts:
            print(f"- {post.title} (by user_id: {post.author_id})")
            # Print a preview of the content (first 50 chars)
            content_preview = post.content[:50] + "..." if len(post.content) > 50 else post.content
            print(f"  Content preview: {content_preview}")

if __name__ == "__main__":
    main() 