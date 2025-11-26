
"""Minimal Flask application setup for the SQLAlchemy assignment."""
from flask import Flask, jsonify, request, redirect, url_for, render_template
from flask_migrate import Migrate
from models import User, Post
from config import Config

# Shared DB extension instance
from database import db

migrate = Migrate()


def create_app(test_config=None):
    """Application factory used by Flask and the tests.

    The optional ``test_config`` dictionary can override settings such as
    the database URL to keep student tests isolated.
    """

    app = Flask(__name__)
    app.config.from_object(Config)
    if test_config:
        app.config.update(test_config)

    db.init_app(app)
    migrate.init_app(app, db)

    # Import models so they're registered with SQLAlchemy
    import models  # noqa: F401

    @app.shell_context_processor
    def make_shell_context():
        return {"db": db, "User": User, "Post": Post}

    @app.before_request
    def init_db():
        """Initialize database with sample data if empty (skip in testing mode)."""
        if app.config.get("TESTING"):
            return

        if User.query.first() is None:
            with app.app_context():
                user1 = User(username="alice", email="alice@example.com")
                user2 = User(username="bob", email="bob@example.com")
                user3 = User(username="charlie", email="charlie@example.com")

                db.session.add_all([user1, user2, user3])
                db.session.commit()

                post1 = Post(
                    title="First Post",
                    content="This is Alice's first post",
                    user_id=user1.id,
                )
                post2 = Post(
                    title="Hello World",
                    content="Bob's introduction to blogging",
                    user_id=user2.id,
                )
                post3 = Post(
                    title="Learning SQLAlchemy",
                    content="Charlie explores database relationships",
                    user_id=user3.id,
                )
                post4 = Post(
                    title="Second Post",
                    content="Alice's second post about Flask",
                    user_id=user1.id,
                )

                db.session.add_all([post1, post2, post3, post4])
                db.session.commit()

    @app.route("/")
    def index():
        """Simple sanity check route."""
        return jsonify({"message": "Welcome to the Flask + SQLAlchemy assignment"})

    @app.route("/verify", methods=["GET"])
    def verify():
        """Verify foreign key relationships between User and Post."""
        users_count = User.query.count()
        posts_count = Post.query.count()

        verify_data = {"users_count": users_count, "posts_count": posts_count, "users": [], "posts": []}

        for user in User.query.all():
            user_data = {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "posts_count": len(user.posts),
                "posts": [{"id": p.id, "title": p.title} for p in user.posts],
            }
            verify_data["users"].append(user_data)

        for post in Post.query.all():
            author = None
            if post.user is not None:
                author = {"id": post.user.id, "username": post.user.username, "email": post.user.email}

            post_data = {
                "id": post.id,
                "title": post.title,
                "content": post.content,
                "user_id": post.user_id,
                "author": author,
            }
            verify_data["posts"].append(post_data)

        return jsonify(verify_data), 200

    @app.route("/users", methods=["GET", "POST"])
    def users():
        """List all users or create a new user."""
        if request.method == "GET":
            user_list = User.query.all()
            result = [
                {"id": user.id, "username": user.username, "email": user.email} for user in user_list
            ]
            return jsonify(result), 200

        data = request.get_json() or {}
        username = data.get("username")
        email = data.get("email")

        if not username:
            return jsonify({"message": "Username is required"}), 400

        new_user = User(username=username, email=email)
        db.session.add(new_user)
        db.session.commit()

        return jsonify({"id": new_user.id, "username": new_user.username, "email": new_user.email}), 201

    @app.route("/users/<int:user_id>", methods=["GET"])
    def get_user(user_id):
        """Get a user by ID."""
        user = db.session.get(User, user_id)
        if not user:
            return jsonify({"message": "User not found"}), 404

        return (
            jsonify(
                {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "posts": [
                        {"id": p.id, "title": p.title, "content": p.content} for p in user.posts
                    ],
                }
            ),
            200,
        )

    @app.route("/users/<int:user_id>/posts", methods=["GET"])
    def get_user_posts(user_id):
        """Get all posts for a specific user."""
        user = db.session.get(User, user_id)
        if not user:
            return jsonify({"message": "User not found"}), 404

        posts = [{"id": p.id, "title": p.title, "content": p.content} for p in user.posts]

        return jsonify({"user_id": user.id, "username": user.username, "posts": posts}), 200

    @app.route("/adduser", methods=["GET"])
    def adduser():
        return render_template("adduser.html")
    @app.route("/adduser", methods=["POST","GET"])
    def add_user():
        if request.method == "POST":
            username = request.form.get("username")
            email = request.form.get("email")

            if not username:
                return render_template("adduser.html", message="Username is required")

            new_user = User(username=username, email=email)
            db.session.add(new_user)
            db.session.commit()

            return redirect(url_for("users"))

        return render_template("adduser.html")
    

    @app.route("/addpost", methods=["GET"])
    def addpost():
        return render_template("addpost.html")
    @app.route("/addpost", methods=["POST","GET"])
    def add_post():
        if request.method == "POST":
            title = request.form.get("title")
            content = request.form.get("content")
            user_id = request.form.get("user_id")

            if not title or not content or not user_id:
                return render_template("addpost.html", message="Title, content, and user_id are required")

            user = db.session.get(User, user_id)
            if not user:
                return render_template("addpost.html", message="User not found")

            new_post = Post(title=title, content=content, user_id=user_id)
            db.session.add(new_post)
            db.session.commit()

            return redirect(url_for("posts"))

        return render_template("addpost.html")

    @app.route("/posts", methods=["GET", "POST"])
    def posts():
        """List or create posts."""
        if request.method == "GET":
            post_list = Post.query.all()
            result = [
                {
                    "id": post.id,
                    "title": post.title,
                    "content": post.content,
                    "user_id": post.user_id,
                    "username": post.user.username if post.user is not None else None,
                }
                for post in post_list
            ]
            return jsonify(result), 200

        data = request.get_json() or {}
        title = data.get("title")
        content = data.get("content")
        user_id = data.get("user_id")

        if not title or not content or not user_id:
            return jsonify({"message": "Title, content, and user_id are required"}), 400

        user = db.session.get(User, user_id)
        if not user:
            return jsonify({"message": "User not found"}), 400

        new_post = Post(title=title, content=content, user_id=user_id)
        db.session.add(new_post)
        db.session.commit()

        return (
            jsonify(
                {
                    "id": new_post.id,
                    "title": new_post.title,
                    "content": new_post.content,
                    "user_id": new_post.user_id,
                    "username": new_post.user.username,
                }
            ),
            201,
        )

    return app


# Expose a module-level application for convenience with certain tools
app = create_app()




if __name__ == "__main__":
            # Running ``python app.py`` starts the development server.
    app.run(debug=True)
