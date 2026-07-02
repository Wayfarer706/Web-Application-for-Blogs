from schemas import PostResponse

posts: list[PostResponse] = [
    PostResponse(
        id=1,
        title="The Future of Web Development",
        content="Exploring how modern frameworks are changing the way we build backend services and APIs.",
        author="Jane Doe",
        date_posted="2026-06-01",
    ),
    PostResponse(
        id=2,
        title="Mastering Jinja Templates",
        content="A deep dive into rendering dynamic HTML pages directly from your Python backend.",
        author="John Smith",
        date_posted="2026-06-02",
    ),
    PostResponse(
        id=3,
        title="Why Type Hints Matter",
        content="Type checking catches bugs before they happen. Here is why you should always strongly type your code.",
        author="Alice Johnson",
        date_posted="2026-06-03",
    ),
]
