from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel
from typing import Optional
from uuid import uuid4

import psycopg
from psycopg.rows import dict_row

app = FastAPI()


########################## Models ##########################


# Post model
class Post(BaseModel):
    title: str
    content: str
    published: bool = True


########################## Methods ##########################


# Get a database connection
def get_db_connection():
    return psycopg.connect(
        host="localhost",
        dbname="blogdb",
        user="bloguser",
        password="blogpassword",
        row_factory=dict_row,
    )


# Find a post
def find_post_by_id(id: int):
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("""SELECT * FROM posts WHERE id = %s""", (id,))
            post = cursor.fetchone()
            if not post:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Post with id {id} not found",
                )
            return post


########################## Routes ##########################


# Root route
@app.get("/")
def read_root():
    return {"message": "Blog API is running"}


@app.get("/posts")
def get_posts():
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("""SELECT * FROM posts""")
            posts = cursor.fetchall()
            return posts


# Get the latest post
@app.get("/posts/latest")
def get_latest_post():
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("""SELECT * FROM posts ORDER BY created_at DESC LIMIT 1""")
            post = cursor.fetchone()
            return post


# Get a single post
@app.get("/posts/{id}")
def get_post(id: int):
    post = find_post_by_id(id)
    return post


# Create a post
@app.post("/posts", status_code=status.HTTP_201_CREATED)
def create_post(post: Post):
    post_dict = post.model_dump()
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """INSERT INTO posts (title, content, published) VALUES (%s, %s, %s) RETURNING *""",
                (post_dict["title"], post_dict["content"], post_dict["published"]),
            )
            new_post = cursor.fetchone()
        conn.commit()
    return {
        "status": "success",
        "message": "Post created successfully",
        "data": new_post,
    }


# Delete a post
@app.delete("/posts/{id}", status_code=status.HTTP_201_CREATED)
def delete_post(id: int):
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("""DELETE FROM posts WHERE id = %s RETURNING *""", (id,))
            deleted_post = cursor.fetchone()
        conn.commit()
    return {
        "status": "success",
        "message": "Post deleted successfully",
        "data": deleted_post,
    }


# Update a post
@app.put("/posts/{id}")
def update_post(id: int, post: Post):
    post_dict = post.model_dump()
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """UPDATE posts SET title = %s, content = %s, published = %s WHERE id = %s RETURNING *""",
                (post_dict["title"], post_dict["content"], post_dict["published"], id),
            )
            updated_post = cursor.fetchone()
        conn.commit()
    return {
        "status": "success",
        "message": "Post updated successfully",
        "data": updated_post,
    }
