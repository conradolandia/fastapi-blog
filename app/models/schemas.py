from pydantic import BaseModel

# Post model for updates
class PostUpdate(BaseModel):
    title: str | None = None
    content: str | None = None
    published: bool = True
