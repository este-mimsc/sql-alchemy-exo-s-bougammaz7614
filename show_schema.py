#!/usr/bin/env python
"""Display database schema and foreign key information."""
import sqlite3
from app import create_app, db
from models import User, Post

app = create_app()

with app.app_context():
    db.create_all()
    
    # Get database file path
    db_url = app.config['SQLALCHEMY_DATABASE_URI']
    db_path = db_url.replace('sqlite:///', '')
    
    # Connect to SQLite database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("=" * 70)
    print("DATABASE SCHEMA - FOREIGN KEY INFORMATION")
    print("=" * 70)
    
    # Get User table info
    print("\n1. USER TABLE SCHEMA:")
    print("-" * 70)
    cursor.execute("PRAGMA table_info(user)")
    columns = cursor.fetchall()
    for col in columns:
        col_id, name, type_, notnull, dflt_value, pk = col
        nullable = "NOT NULL" if notnull else "NULLABLE"
        primary = "PRIMARY KEY" if pk else ""
        print(f"   {name:<15} {type_:<10} {nullable:<10} {primary}")
    
    # Get Post table info
    print("\n2. POST TABLE SCHEMA:")
    print("-" * 70)
    cursor.execute("PRAGMA table_info(posts)")
    columns = cursor.fetchall()
    for col in columns:
        col_id, name, type_, notnull, dflt_value, pk = col
        nullable = "NOT NULL" if notnull else "NULLABLE"
        primary = "PRIMARY KEY" if pk else ""
        print(f"   {name:<15} {type_:<10} {nullable:<10} {primary}")
    
    # Get foreign keys
    print("\n3. FOREIGN KEY CONSTRAINTS IN POST TABLE:")
    print("-" * 70)
    cursor.execute("PRAGMA foreign_key_list(posts)")
    fks = cursor.fetchall()
    for fk in fks:
        id_, seq, table, from_col, to_col, on_delete, on_update, match = fk
        print(f"   Column: {from_col}")
        print(f"   References: {table}.{to_col}")
        print(f"   On Delete: {on_delete}")
        print(f"   On Update: {on_update}")
    
    # Verify foreign key constraint
    print("\n4. FOREIGN KEY INTEGRITY CHECK:")
    print("-" * 70)
    
    cursor.execute("SELECT COUNT(*) FROM posts WHERE user_id NOT IN (SELECT id FROM user)")
    orphaned = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM posts")
    total_posts = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM user")
    total_users = cursor.fetchone()[0]
    
    print(f"   Total Users: {total_users}")
    print(f"   Total Posts: {total_posts}")
    print(f"   Orphaned Posts (invalid FK): {orphaned}")
    
    if orphaned == 0 and total_posts > 0:
        print(f"\n   ✓ ALL {total_posts} POSTS HAVE VALID FOREIGN KEYS")
    elif total_posts == 0:
        print(f"\n   ℹ No posts in database yet (table is empty)")
    else:
        print(f"\n   ✗ WARNING: {orphaned} posts have invalid foreign keys")
    
    print("\n" + "=" * 70)
    print("SAMPLE DATA RELATIONSHIPS:")
    print("-" * 70)
    
    cursor.execute("""
    SELECT u.id, u.username, COUNT(p.id) as post_count
    FROM user u
    LEFT JOIN posts p ON u.id = p.user_id
    GROUP BY u.id, u.username
    ORDER BY u.id
    """)
    
    relationships = cursor.fetchall()
    for user_id, username, post_count in relationships:
        print(f"   User #{user_id} ({username}): {post_count} posts")
    
    print("\n" + "=" * 70)
    
    conn.close()
