import asyncio
import random
from datetime import UTC, datetime, timedelta
from typing import TypedDict

import httpx
from sqlalchemy import delete, select, text, update

from config import settings
from database import AsyncSessionLocal, Base, engine
from enums import UserRole
from image_utils import _get_s3_client  # pyright: ignore[reportPrivateUsage]
from main import app
from models.category import Category
from models.comment import Comment
from models.password_reset_token import PasswordResetToken
from models.post import Post
from models.tag import Tag
from models.user import User


class PopulatedUser(TypedDict):
    id: int
    username: str
    token: str
    role: str


class UserData(TypedDict):
    username: str
    email: str
    password: str
    use_avatar: bool
    role: UserRole


class PostData(TypedDict):
    title: str
    content: str


USERS: list[UserData] = [
    {
        "username": "JaneDoe",
        "email": "JaneDoe@gmail.com",
        "password": "TestPassword1!",
        "use_avatar": True,
        "role": UserRole.ADMIN,
    },
    {
        "username": "DefaultDude",
        "email": "TestEmail2@test.com",
        "password": "TestPassword2!",
        "use_avatar": False,
        "role": UserRole.EDITOR,
    },
    {
        "username": "WillowTheCat",
        "email": "TestEmail3@test.com",
        "password": "TestPassword3!",
        "use_avatar": True,
        "role": UserRole.USER,
    },
    {
        "username": "Dog",
        "email": "TestEmail4@test.com",
        "password": "TestPassword4!",
        "use_avatar": True,
        "role": UserRole.USER,
    },
    {
        "username": "Someone",
        "email": "TestEmail5@test.com",
        "password": "TestPassword5!",
        "use_avatar": True,
        "role": UserRole.USER,
    },
    {
        "username": "StrangeFace",
        "email": "TestEmail6@test.com",
        "password": "TestPassword6!",
        "use_avatar": True,
        "role": UserRole.USER,
    },
]

CATEGORIES: list[str] = [
    "Python & FastAPI",
    "Web Development",
    "Gaming & Hobbies",
    "Personal Thoughts",
    "Software Engineering",
]

TAGS: list[str] = [
    "fastapi",
    "python",
    "async",
    "tutorial",
    "review",
    "sqlalchemy",
    "pydantic",
    "backend",
    "coding",
    "lifestyle",
]

POSTS: list[PostData] = [
    {
        "title": "Why I Love FastAPI",
        "content": "FastAPI has completely changed how I build modern web services. The automatic OpenAPI documentation, native Python type hints, and first-class asynchronous support make development significantly faster and more enjoyable. Plus, the performance is on par with NodeJS and Go.",
    },
    {
        "title": "Why Good Documentation is a Developer's Best Friend",
        "content": "When evaluating a new library or framework, the quality of its documentation is often my primary deciding factor. Clear getting-started guides, interactive API schemas, and comprehensive code examples reduce the learning curve drastically and save teams countless engineering hours.",
    },
    {
        "title": "Async and Await Finally Clicked",
        "content": "I struggled with asynchronous programming concepts for months, but working with modern Python web frameworks finally made it click. Using 'async def' for non-blocking network endpoints and 'await' for database input/output operations creates a smooth, highly concurrent architecture.",
    },
    {
        "title": "Managing Burnout in Software Engineering",
        "content": "In an industry where technology evolves daily, the pressure to constantly upskill can be overwhelming. It is essential to recognize the early signs of technical burnout. Step away from the keyboard, prioritize physical health, and remember that taking breaks is part of sustainable engineering.",
    },
    {
        "title": "Pydantic Validation is Absolutely Brilliant",
        "content": "The way Pydantic handles data validation and serialization is a game changer for Python development. You define your domain schemas once using standard type hints, and the library automatically handles parsing, validation, and error reporting. No more writing manual validation boilerplate.",
    },
    {
        "title": "From Flask to FastAPI: A Transition Guide",
        "content": "Our team recently transitioned several core microservices from Flask to FastAPI. The migration was remarkably smooth due to similar routing paradigms, but the immediate benefits were substantial: automated API documentation, stricter request validation, and noticeable performance improvements under load.",
    },
    {
        "title": "Some of My Favorite Horror Movies",
        "content": "I have always been a huge fan of psychological thriller and horror cinema, particularly films that utilize practical effects over CGI. One of my absolute favorites is John Carpenter's 'The Thing'. For a more modern recommendation, 'The Night House' is a brilliant slow burn that relies heavily on atmospheric tension rather than inexpensive jump scares.",
    },
    {
        "title": "Type Hints Changed My Python Codebase",
        "content": "I used to view Python type hints as unnecessary overhead that slowed down initial scripting. However, after adopting them across a large collaborative codebase, I see their immense value. They enable superior IDE autocomplete, catch type-mismatch bugs during static analysis, and serve as built-in documentation.",
    },
    {
        "title": "The Power of Dependency Injection",
        "content": "A clean dependency injection system separates component creation from business logic. Whether you need a database session, an authenticated user context, or a third-party API client, injecting dependencies into route handlers makes your application architecture decoupled, modular, and easy to unit test.",
    },
    {
        "title": "SQLAlchemy 2.0 Is Worth the Upgrade",
        "content": "If your projects are still relying on legacy SQLAlchemy 1.x query patterns, it is time to plan an upgrade. The 2.0 syntax, which relies on explicit select() statements and mapped_column() annotations, aligns beautifully with modern asynchronous Python execution.",
    },
    {
        "title": "Hot Take: Python Beats Node.js for Backend APIs",
        "content": "When it comes to building scalable backend APIs, modern Python frameworks combined with ASGI servers provide a developer experience that rivals or surpasses Node.js. The clarity of the syntax and the robustness of the data validation ecosystem make maintenance a breeze. Let us know where you stand in the comments below!",
    },
    {
        "title": "Understanding HTTP Status Codes",
        "content": "200 OK, 201 Created, 400 Bad Request, 403 Forbidden, 404 Not Found, 500 Internal Server Error. Learning standard HTTP semantics is crucial for building predictable REST APIs. Every code communicates a specific structural state to frontend applications and consuming clients.",
    },
    {
        "title": "Some of My Favorite Video Games",
        "content": "My gaming rotation leans heavily toward single-player RPGs that offer deep world-building and player agency. The Elder Scrolls series, particularly Morrowind and Skyrim, holds a special place in my gaming history. I also love classic isometric RPGs like Baldur's Gate, Pillars of Eternity, and Pathfinder: Wrath of the Righteous.",
    },
    {
        "title": "JWT Authentication Demystified",
        "content": "JSON Web Tokens can feel intimidating initially, but the underlying concept is straightforward. A server signs a payload containing user claims using a cryptographic secret. The client stores this token and includes it in subsequent request headers, allowing stateless, distributed authentication across web services.",
    },
    {
        "title": "Core Principles for Clean API Design",
        "content": "When designing RESTful systems, always use plural nouns for resource URLs (/users, /posts), rely on standard HTTP verbs for CRUD operations (GET, POST, PATCH, DELETE), and maintain a consistent error-reporting schema across your endpoints.",
    },
    {
        "title": "Path Parameters vs Query Parameters",
        "content": "Understanding resource routing is fundamental to API design. Use path parameters for required resource identifiers, such as /users/123. Use query parameters for optional filtering, sorting, and pagination, such as /posts?category=python&limit=10.",
    },
    {
        "title": "Error Handling Done Right",
        "content": "Never allow your application to fail silently or return generic 500 Internal Server Error codes for client-side mistakes. Catch exceptions cleanly and return descriptive, structured HTTP error responses so frontend developers can easily debug integration issues.",
    },
    {
        "title": "Why I Switched to the UV Package Manager",
        "content": "The Python packaging ecosystem has evolved rapidly, and the UV tool has been a massive quality-of-life upgrade for my local development workflow. It resolves dependency trees and installs virtual environments in milliseconds, drastically cutting down CI/CD pipeline execution times.",
    },
    {
        "title": "My Favorite Non-Fiction Reads",
        "content": "While I occasionally enjoy hard science fiction like Andy Weir's 'The Martian', my reading list consists primarily of philosophy and non-fiction. Some books I return to regularly include 'Meditations' by Marcus Aurelius, 'How to Die' by Seneca, and Randy Pausch's inspiring 'The Last Lecture'.",
    },
    {
        "title": "Testing Strategies for Backend Applications",
        "content": "Writing robust automated tests is non-negotiable for production systems. Leveraging isolated database clients, mocking external API integrations, and testing both happy paths and edge-case validation failures ensures your application remains stable as the codebase scales.",
    },
    {
        "title": "Environment Variables and Application Security",
        "content": "Never commit secrets, database connection strings, or encryption keys to version control. Utilize application settings managers to load environment variables dynamically, ensuring complete separation between local development configs and live production deployments.",
    },
    {
        "title": "Taming CORS in Distributed Architectures",
        "content": "Cross-Origin Resource Sharing (CORS) is a vital browser security feature that often frustrates frontend developers during API integration. The key to handling it cleanly is explicitly whitelisting trusted frontend origins rather than using wildcard policies in production environments.",
    },
    {
        "title": "Optimizing Asynchronous Database Queries",
        "content": "Executing synchronous, blocking database calls within an asynchronous event loop can severely degrade server performance. Utilizing modern async database drivers, such as psycopg for PostgreSQL or aiosqlite, ensures your application handles high concurrency without freezing worker threads.",
    },
    {
        "title": "The Security Benefits of Strict Response Models",
        "content": "Response serialization models serve a dual purpose: they provide clear contract documentation for API consumers, and they act as a security layer by automatically filtering out sensitive internal database fields like password hashes or internal audit timestamps.",
    },
    {
        "title": "Let's Talk Tabletop Board Games",
        "content": "Tabletop gaming is one of my favorite ways to disconnect from technology. Classic strategy games like Settlers of Catan remain tabletop staples for game nights. I have also been getting into immersive Dungeons & Dragons campaigns, which offer unparalleled storytelling and collaborative problem-solving.",
    },
    {
        "title": "API Versioning Strategies for Long-Term Growth",
        "content": "Public APIs evolve over time. Implementing a clear versioning strategy from day one—whether through URL prefixing like /v1/users or via custom HTTP request headers—ensures you can roll out breaking database and schema changes without disrupting existing integrations.",
    },
    {
        "title": "Offloading Work with Background Tasks",
        "content": "Web applications should never keep a client waiting for slow, secondary operations to finish. Sending transactional emails, generating PDF reports, or resizing uploaded images should always be pushed to background task queues or asynchronous worker threads.",
    },
    {
        "title": "Protecting Your Infrastructure with Rate Limiting",
        "content": "Implementing rate limiting on public endpoints is essential for preventing automated scraping, brute-force authentication attacks, and denial-of-service attempts. Return a clean 429 Too Many Requests status code when clients exceed their allocated request bursts.",
    },
    {
        "title": "Writing Self-Documenting Code",
        "content": "Code is read far more often than it is written. Investing time in clear variable naming, comprehensive docstrings, and explicit schema examples ensures that your codebase remains approachable for onboarding engineers and future maintainers.",
    },
    {
        "title": "Real-Time Communication with WebSockets",
        "content": "While traditional REST architecture excels at stateless request-response workflows, interactive features like live group chat, notification feeds, and real-time dashboard analytics require persistent, bi-directional WebSocket connections.",
    },
    {
        "title": "Finding Balance Through Woodworking",
        "content": "Outside of software engineering, my favorite creative outlet is woodworking. There is something deeply rewarding about stepping away from abstract digital systems and working with physical materials to build tangible, functional furniture by hand.",
    },
    {
        "title": "Implementing Complex Domain Validation",
        "content": "While basic type checking catches simple input errors, real-world business logic often requires complex domain validation. Utilizing model-level validation hooks allows you to enforce multi-field dependencies, verify password complexity rules, and sanitize input strings before they hit the database.",
    },
    {
        "title": "The ORM vs Raw SQL Debate",
        "content": "Object-Relational Mappers provide excellent developer ergonomics and protect against SQL injection out of the box. However, high-performance reporting dashboards or complex aggregations often benefit from dropping down to raw, optimized SQL queries. A balanced engineering team knows when to leverage both.",
    },
    {
        "title": "Debugging Asynchronous Execution Flows",
        "content": "Tracing bugs across asynchronous execution loops requires a systematic approach. Structured logging with unique correlation IDs, proper exception handling across concurrent tasks, and an understanding of context variables are vital tools for diagnosing production anomalies.",
    },
    {
        "title": "Containerization and Deployment Consistency",
        "content": "Packaging application services inside Docker containers guarantees parity across local development machines, staging environments, and production clusters. Containerization eliminates the dreaded 'it works on my machine' class of infrastructure bugs.",
    },
    {
        "title": "The Importance of Automated Health Checks",
        "content": "Every cloud-native backend service should expose a lightweight /health endpoint. Container orchestration platforms like Kubernetes and cloud load balancers rely on these probes to automatically route traffic away from failing instances and trigger container self-healing.",
    },
    {
        "title": "The Value of Collaborative Code Reviews",
        "content": "Code reviews should be approached as an opportunity for mentorship and knowledge sharing rather than a gatekeeping exercise. Constructive peer review catches architectural oversights early, promotes coding consistency, and builds a culture of shared code ownership.",
    },
    {
        "title": "Designing Efficient Pagination Systems",
        "content": "Returning unpaginated database collections is a major performance hazard that can cause severe memory spikes on both client devices and backend servers. Always enforce sensible limit and offset defaults, or implement cursor-based pagination for high-volume data streams.",
    },
    {
        "title": "Customizing OpenAPI Schema Output",
        "content": "A well-structured API schema is a powerful developer tool. Taking the time to add detailed endpoint descriptions, categorization tags, and realistic response payloads makes integrating with your backend an intuitive experience for frontend teams and third-party consumers.",
    },
    {
        "title": "Securing Web Applications with HTTP Headers",
        "content": "Configuring standard HTTP security headers is a low-effort, high-impact defense mechanism. Properly tuned headers like Content-Security-Policy, X-Content-Type-Options, and X-Frame-Options help mitigate cross-site scripting and clickjacking vulnerabilities.",
    },
    {
        "title": "Implementing Effective Caching Layers",
        "content": "Repeatedly querying immutable or slow-changing data directly from disk-based databases creates unnecessary latency. Introducing an in-memory caching layer with Redis or Memcached reduces database load drastically and drops API response times into the single-digit milliseconds.",
    },
    {
        "title": "Choosing Between REST and GraphQL",
        "content": "Neither REST nor GraphQL is a universal silver bullet. REST provides architectural simplicity, superior HTTP caching capabilities, and clear resource boundaries. GraphQL shines in complex client applications where frontends need to aggregate nested data across multiple entities in a single network trip.",
    },
    {
        "title": "How Science Fiction Inspired My Engineering Career",
        "content": "'You wanna know how I did it? This is how I did it, Anton. I never saved anything for the swim back.' This classic quote from the film Gattaca has always resonated with me. The movie's themes of determination and passion pushed me to apply for an engineering internship during college. That experience instilled a relentless drive to understand complex technology, eventually leading me to my career in software development.",
    },
]

POST_44: PostData = {
    "title": "Fun Fact: My High School Football Number Was #44",
    "content": "To wrap up our initial collection of blog posts, here is a piece of personal sports trivia: my high school football jersey number was #44. I share that number with some absolute legends across professional sports, including NBA icon Jerry West, MLB home run king Hank Aaron, and NFL hall-of-famer Floyd Little.",
}


async def clear_existing_data() -> None:
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(User.image_file).where(User.image_file.is_not(None)),
        )
        filenames = result.scalars().all()

    if filenames:
        s3 = _get_s3_client()
        s3.delete_objects(
            Bucket=settings.s3_bucket_name,
            Delete={"Objects": [{"Key": f"profile_pics/{f}"} for f in filenames]},
        )
        print(f"Deleted {len(filenames)} images from S3")

    # Order respects foreign key constraints across all domains
    async with AsyncSessionLocal() as db:
        await db.execute(text("DELETE FROM post_tag"))
        await db.execute(delete(Post))
        await db.execute(delete(Tag))
        await db.execute(delete(Category))
        await db.execute(delete(PasswordResetToken))
        await db.execute(delete(User))
        await db.commit()
    print("Cleared existing data")


async def update_post_dates() -> None:
    now = datetime.now(UTC)

    async with AsyncSessionLocal() as db:
        result = await db.execute(select(Post).order_by(Post.id))
        posts = result.scalars().all()

        if not posts:
            return

        await db.execute(
            update(Post)
            .where(Post.id == posts[0].id)
            .values(date_posted=now - timedelta(days=90)),
        )

        for i, post in enumerate(posts[1:], start=1):
            days_ago = (len(posts) - i) * 1.5
            hours_offset = (i * 7) % 24
            post_date = now - timedelta(days=days_ago, hours=hours_offset)
            await db.execute(
                update(Post).where(Post.id == post.id).values(date_posted=post_date),
            )

        await db.commit()
    print("Updated post dates")


async def elevate_user_roles() -> None:
    print("\nElevating specific user roles...")
    async with AsyncSessionLocal() as db:
        for user_data in USERS:
            if user_data["role"] != UserRole.USER:
                await db.execute(
                    update(User)
                    .where(User.username == user_data["username"])
                    .values(role=user_data["role"]),
                )
                print(
                    f"  Elevated {user_data['username']} to {user_data['role'].value}"
                )
        await db.commit()


async def create_users(client: httpx.AsyncClient) -> list[PopulatedUser]:
    users: list[PopulatedUser] = []
    print(f"\nCreating {len(USERS)} users...")

    for user_data in USERS:
        response = await client.post(
            "/api/users",
            json={
                "username": user_data["username"],
                "email": user_data["email"],
                "password": user_data["password"],
            },
        )
        response.raise_for_status()
        user = response.json()
        print(f"  Created: {user['username']}")

        response = await client.post(
            "/api/users/token",
            data={
                "username": user_data["email"],
                "password": user_data["password"],
            },
        )
        response.raise_for_status()
        token = response.json()["access_token"]

        if user_data.get("use_avatar"):
            avatar_url = f"https://ui-avatars.com/api/?name={user['username']}&size=200&background=random"

            async with httpx.AsyncClient() as dl_client:
                img_response = await dl_client.get(avatar_url)
                img_response.raise_for_status()
                image_bytes = img_response.content

            response = await client.patch(
                f"/api/users/{user['id']}/picture",
                files={
                    "file": (
                        f"{user['username']}_avatar.png",
                        image_bytes,
                        "image/png",
                    ),
                },
                headers={"Authorization": f"Bearer {token}"},
            )
            response.raise_for_status()
            print(f"    Uploaded dynamic avatar to S3 for: {user['username']}")

        users.append(
            {
                "id": user["id"],
                "username": user["username"],
                "token": token,
                "role": user_data["role"].value,
            }
        )

    await elevate_user_roles()
    return users


async def create_categories(client: httpx.AsyncClient, admin_token: str) -> list[int]:
    print(f"\nCreating {len(CATEGORIES)} categories...")
    category_ids: list[int] = []

    for name in CATEGORIES:
        response = await client.post(
            "/api/categories",
            json={"name": name},
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        response.raise_for_status()
        category_ids.append(response.json()["id"])
        print(f"  Created category: {name}")

    return category_ids


async def create_tags(client: httpx.AsyncClient, admin_token: str) -> list[int]:
    print(f"\nCreating {len(TAGS)} tags...")
    tag_ids: list[int] = []

    for name in TAGS:
        response = await client.post(
            "/api/tags",
            json={"name": name},
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        response.raise_for_status()
        tag_ids.append(response.json()["id"])
        print(f"  Created tag: {name}")

    return tag_ids


async def create_posts(
    client: httpx.AsyncClient,
    users: list[PopulatedUser],
    category_ids: list[int],
    tag_ids: list[int],
) -> list[int]:
    print(f"\nCreating {len(POSTS) + 1} posts with categories and tags...")
    post_ids: list[int] = []

    response = await client.post(
        "/api/posts",
        json={
            "title": POST_44["title"],
            "content": POST_44["content"],
            "category_id": random.choice(category_ids),
            "tag_ids": random.sample(
                tag_ids, k=random.randint(1, min(3, len(tag_ids)))
            ),
        },
        headers={"Authorization": f"Bearer {users[0]['token']}"},
    )
    response.raise_for_status()
    post_ids.append(response.json()["id"])
    print(f"  Created: '{POST_44['title']}'")

    for i, post_data in enumerate(reversed(POSTS)):
        user = users[i % len(users)]
        response = await client.post(
            "/api/posts",
            json={
                "title": post_data["title"],
                "content": post_data["content"],
                "category_id": random.choice(category_ids),
                "tag_ids": random.sample(
                    tag_ids, k=random.randint(1, min(3, len(tag_ids)))
                ),
            },
            headers={"Authorization": f"Bearer {user['token']}"},
        )
        response.raise_for_status()
        post_ids.append(response.json()["id"])
        title = post_data["title"]
        print(
            f"  Created: '{title[:50]}...'"
            if len(title) > 50
            else f"  Created: '{title}'",
        )

    return post_ids


async def create_comments(
    client: httpx.AsyncClient, users: list[PopulatedUser], post_ids: list[int]
) -> None:
    print("\nCreating top-level comments and replies...")

    # Seed discussions across a subset of posts
    for post_id in post_ids[:15]:
        author = random.choice(users)
        response = await client.post(
            "/api/comments",
            json={
                "post_id": post_id,
                "content": "This is a really insightful article. Thanks for putting this together!",
                "parent_id": None,
            },
            headers={"Authorization": f"Bearer {author['token']}"},
        )
        response.raise_for_status()
        parent_comment = response.json()
        print(f"  Created comment on Post ID {post_id}")

        # Add 1 to 2 replies to the top-level comment
        for _ in range(random.randint(1, 2)):
            replier = random.choice(users)
            reply_response = await client.post(
                "/api/comments",
                json={
                    "post_id": post_id,
                    "content": "I completely agree with your thoughts here!",
                    "parent_id": parent_comment["id"],
                },
                headers={"Authorization": f"Bearer {replier['token']}"},
            )
            reply_response.raise_for_status()
            print(f"    Created reply to Comment ID {parent_comment['id']}")


async def populate() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    transport = httpx.ASGITransport(app=app)

    async with httpx.AsyncClient(
        transport=transport,
        base_url="http://localhost",
    ) as client:
        await clear_existing_data()

        users = await create_users(client)

        # Locate the admin token for CUD operations on global resources
        admin_token = next(
            u["token"] for u in users if u["role"] == UserRole.ADMIN.value
        )

        category_ids = await create_categories(client, admin_token)
        tag_ids = await create_tags(client, admin_token)
        post_ids = await create_posts(client, users, category_ids, tag_ids)
        await create_comments(client, users, post_ids)

        print("\nUpdating post dates...")
        await update_post_dates()

    await engine.dispose()

    print("\nDone!")
    print(f"  {len(USERS)} users generated with hierarchical roles")
    print(f"  {len(CATEGORIES)} categories generated")
    print(f"  {len(TAGS)} tags generated")
    print(f"  {len(POSTS) + 1} posts generated with relational links")
    print("  Discussions and nested replies seeded across posts")


if __name__ == "__main__":
    asyncio.run(populate())
