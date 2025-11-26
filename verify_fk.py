#!/usr/bin/env python
"""Verify foreign key relationships between User and Post tables."""
import json
from app import create_app, db
from models import User, Post

# Create app context
app = create_app()

with app.app_context():
    # Create all tables
    db.create_all()
    
    # Initialize sample data if not already present
    if User.query.count() == 0:
        # Create sample users
        user1 = User(username="alice", email="alice@example.com")
        user2 = User(username="bob", email="bob@example.com")
        user3 = User(username="charlie", email="charlie@example.com")
        
        db.session.add_all([user1, user2, user3])
        db.session.commit()
        
        # Create sample posts linked to users
        post1 = Post(title="First Post", content="This is Alice's first post", user_id=user1.id)
        post2 = Post(title="Hello World", content="Bob's introduction to blogging", user_id=user2.id)
        post3 = Post(title="Learning SQLAlchemy", content="Charlie explores database relationships", user_id=user3.id)
        post4 = Post(title="Second Post", content="Alice's second post about Flask", user_id=user1.id)
        
        db.session.add_all([post1, post2, post3, post4])
        db.session.commit()
    
    # Verification report
    verify_data = {
        "users_count": User.query.count(),
        "posts_count": Post.query.count(),
        "users": [],
        "posts": []
    }
    
    # Show users and their posts
    print("=" * 60)
    print("FOREIGN KEY VERIFICATION REPORT")
    print("=" * 60)
    print(f"\nTotal Users: {verify_data['users_count']}")
    print(f"Total Posts: {verify_data['posts_count']}\n")
    
    print("USERS WITH THEIR POSTS:")
    print("-" * 60)
    for user in User.query.all():
        user_data = {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "posts_count": len(user.posts),
            "posts": [{"id": p.id, "title": p.title} for p in user.posts]
        }
        verify_data["users"].append(user_data)
        print(f"User #{user.id}: {user.username} ({user.email})")
        print(f"  Posts: {len(user.posts)}")
        for post in user.posts:
            print(f"    - Post #{post.id}: {post.title}")
    
    print("\n" + "=" * 60)
    print("ALL POSTS WITH AUTHOR INFORMATION:")
    print("-" * 60)
    for post in Post.query.all():
        post_data = {
            "id": post.id,
            "title": post.title,
            "content": post.content,
            "user_id": post.user_id,
            "author": {
                "id": post.user.id,
                "username": post.user.username,
                "email": post.user.email
            }
        }
        verify_data["posts"].append(post_data)
        print(f"Post #{post.id}: {post.title}")
        print(f"  Content: {post.content}")
        print(f"  Author: {post.user.username} (User #{post.user.id})")
        print(f"  Foreign Key (user_id): {post.user_id}")
    
    print("\n" + "=" * 60)
    print("FOREIGN KEY VALIDATION:")
    print("-" * 60)
    
    # Validate all posts have valid user_id
    valid_fk = True
    for post in Post.query.all():
        user = db.session.get(User, post.user_id)
        if user:
            print(f"✓ Post #{post.id} correctly references User #{post.user_id}")
        else:
            print(f"✗ Post #{post.id} has invalid user_id: {post.user_id}")
            valid_fk = False
    
    print("\n" + "=" * 60)
    if valid_fk and verify_data['users_count'] > 0 and verify_data['posts_count'] > 0:
        print("✓ ALL FOREIGN KEYS ARE VALID")
        print("✓ SAMPLE DATA SUCCESSFULLY LOADED")
    else:
        print("✗ FOREIGN KEY VALIDATION FAILED")
    print("=" * 60)
    
    # Print JSON output
    print("\nJSON OUTPUT:")
    print(json.dumps(verify_data, indent=2))
