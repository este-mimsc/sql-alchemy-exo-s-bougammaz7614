content = '''"""Flask application factory and minimal routes for the SQLAlchemy exercise.

This file provides a single, well-formed `create_app` factory used by the
tests. It exports `create_app` and re-exports the `db` extension instance so
that tests can import them from `app`.
"""
from flask import Flask, jsonify, request
from flask_migrate import Migrate

from config import Config
from database import db
from models import User, Post

migrate = Migrate()


def create_app(test_config=None):
    """Application factory.

    The optional `test_config` dict can override configuration values for
    tests (for example the in-memory SQLite URL).
    """

    app = Flask(__name__)
    app.config.from_object(Config)
    if test_config:
        app.config.update(test_config)

    db.init_app(app)
    migrate.init_app(app, db)

    # Ensure models are imported/registered
    import models  # noqa: F401

    @app.shell_context_processor
    def make_shell_context():
        return {"db": db, "User": User, "Post": Post}

    @app.route("/")
    def index():
        return jsonify({"message": "Welcome to the Flask + SQLAlchemy assignment"})

    @app.route("/users", methods=["GET", "POST"])
    def users():
        if request.method == "GET":
            users = User.query.all()
            payload = [
                {"id": u.id, "username": u.username, "email": u.email} for u in users
            ]
            return jsonify(payload), 200

        data = request.get_json() or {}
        username = data.get("username")
        email = data.get("email")

        if not username:
            return jsonify({"message": "Username is required"}), 400

        new_user = User(username=username, email=email)
        db.session.add(new_user)
        db.session.commit()

        return (
            jsonify({"id": new_user.id, "username": new_user.username, "email": new_user.email}),
            201,
        )

    @app.route("/users/<int:user_id>", methods=["GET"])
    def get_user(user_id):
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
        user = db.session.get(User, user_id)
        if not user:
            return jsonify({"message": "User not found"}), 404

        posts = [{"id": p.id, "title": p.title, "content": p.content} for p in user.posts]
        return jsonify({"user_id": user.id, "username": user.username, "posts": posts}), 200

    @app.route("/posts", methods=["GET", "POST"])
    def posts():
        if request.method == "GET":
            posts = Post.query.all()
            payload = [
                {
                    "id": p.id,
                    "title": p.title,
                    "content": p.content,
                    "user_id": p.user_id,
                    "username": p.user.username if p.user is not None else None,
                }
                for p in posts
            ]
            return jsonify(payload), 200

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


# Expose the db extension and a module-level app for convenience
app = create_app()


if __name__ == "__main__":
    app.run(debug=True)
'''

open('app.py','w', encoding='utf-8').write(content)
print('wrote app.py')
