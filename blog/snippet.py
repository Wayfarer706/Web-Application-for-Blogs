from pydantic import BaseModel


class Post(BaseModel):
    id: int
    title: str
    content: str
    date_posted: str


posts: list[Post] = [
    Post(
        id=1,
        title="The Future of Web Development",
        content="Exploring how modern frameworks are changing the way we build backend services and APIs.",
        date_posted="2026-06-01",
    ),
    Post(
        id=2,
        title="Mastering Jinja Templates",
        content="A deep dive into rendering dynamic HTML pages directly from your Python backend.",
        date_posted="2026-06-02",
    ),
    Post(
        id=3,
        title="Why Type Hints Matter",
        content="Type checking catches bugs before they happen. Here is why you should always strongly type your code.",
        date_posted="2026-06-03",
    ),
]
