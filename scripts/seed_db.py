#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import random
from datetime import timezone


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

from faker import Faker
from sqlmodel import SQLModel
from app.database import engine, get_session
from app.models.user_model import User
from app.models.post_model import Post
from app.utils.security import hash_password


# Initialize Faker
fake = Faker()


def drop_and_create_tables():
    """Drop all tables and recreate them"""
    print("Dropping all tables...")
    SQLModel.metadata.drop_all(engine)
    
    print("Creating all tables...")
    SQLModel.metadata.create_all(engine)


def create_users(n=5):
    """Create n random users with a common password"""
    print(f"Creating {n} users...")
    users = []
    common_password = "password123"
    hashed_password = hash_password(common_password)
    
    with next(get_session()) as session:
        for _ in range(n):
            username = fake.user_name()
            email = fake.email()
            
            # Make sure username and email are unique
            while any(u.username == username or u.email == email for u in users):
                username = fake.user_name()
                email = fake.email()
            
            user = User(
                username=username,
                email=email,
                password=hashed_password,
                created_at=fake.date_time_between(
                    start_date="-1y", end_date="now", tzinfo=timezone.utc
                ),
            )
            session.add(user)
            users.append(user)
        
        session.commit()
        
        # Refresh all users to get their IDs
        for user in users:
            session.refresh(user)
    
    return users


def create_posts(users, n=20):
    """Create n random posts assigned to random users"""
    print(f"Creating {n} posts...")
    with next(get_session()) as session:
        for _ in range(n):
            user = random.choice(users)
            created_at = fake.date_time_between(
                start_date=user.created_at, 
                end_date="now", 
                tzinfo=timezone.utc
            )
            updated_at = created_at
            
            # 25% chance to have an update time later than creation time
            if random.random() < 0.25:
                updated_at = fake.date_time_between(
                    start_date=created_at,
                    end_date="now",
                    tzinfo=timezone.utc
                )
            
            # Generate paragraphs and join them with newlines
            paragraphs = fake.paragraphs(nb=random.randint(1, 5))
            content = "\n\n".join(paragraphs)
            
            post = Post(
                title=fake.sentence(nb_words=6, variable_nb_words=True),
                content=content,
                published=random.choice([True, True, True, False]),  # 75% published
                author_id=user.id,
                created_at=created_at,
                updated_at=updated_at,
            )
            session.add(post)
        
        session.commit()


def seed_db(num_users=5, num_posts=20):
    """Main function to seed the database"""
    drop_and_create_tables()
    users = create_users(n=num_users)
    create_posts(users, n=num_posts)
    print("Database seeded successfully!")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Seed the database with random data")
    parser.add_argument("--users", type=int, default=5, help="Number of users to create")
    parser.add_argument("--posts", type=int, default=20, help="Number of posts to create")
    
    args = parser.parse_args()
    
    seed_db(num_users=args.users, num_posts=args.posts) 