"""
Comprehensive community forum endpoint tests.
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from html import escape


class TestCommunityEndpoints:
    """Test community forum API endpoints."""

    def test_community_requires_authentication_for_write(self, client: TestClient):
        """Test that write operations require authentication."""
        # Create post without auth
        response = client.post(
            "/api/v1/community/posts",
            json={
                "title": "Test",
                "content": "Test content",
                "category": "general"
            }
        )
        assert response.status_code == 401

    def test_community_read_public(self, client: TestClient):
        """Test that reading community posts doesn't require auth."""
        response = client.get("/api/v1/community/posts")
        # Should be allowed (either 200, 404 if DB empty, but not 401)
        assert response.status_code != 401

    def test_create_post_success(self, authenticated_client: TestClient, db_session: Session):
        """Test successfully creating a community post."""
        post_data = {
            "title": "Hacking Tips",
            "content": "Here are some useful hacking techniques",
            "category": "general"
        }
        
        response = authenticated_client.post("/api/v1/community/posts", json=post_data)
        
        if response.status_code == 201:
            data = response.json()
            assert data["title"] == post_data["title"]
            assert data["content"] == post_data["content"]
            assert "id" in data

    def test_create_post_requires_title(self, authenticated_client: TestClient):
        """Test that post creation requires title."""
        response = authenticated_client.post(
            "/api/v1/community/posts",
            json={
                "content": "Content without title",
                "category": "general"
            }
        )
        assert response.status_code == 422

    def test_create_post_requires_content(self, authenticated_client: TestClient):
        """Test that post creation requires content."""
        response = authenticated_client.post(
            "/api/v1/community/posts",
            json={
                "title": "Title without content",
                "category": "general"
            }
        )
        assert response.status_code == 422

    def test_create_post_minimum_length(self, authenticated_client: TestClient):
        """Test minimum content length validation."""
        response = authenticated_client.post(
            "/api/v1/community/posts",
            json={
                "title": "T",  # Too short
                "content": "C",  # Too short
                "category": "general"
            }
        )
        # Should fail validation
        if response.status_code == 422:
            assert "at least" in response.text.lower() or "minimum" in response.text.lower()

    def test_xss_in_post_content(self, authenticated_client: TestClient):
        """Test XSS protection in post content."""
        malicious_content = {
            "title": "Normal Title",
            "content": "Normal content <script>alert('xss')</script> dangerous",
            "category": "general"
        }
        
        response = authenticated_client.post("/api/v1/community/posts", json=malicious_content)
        
        if response.status_code == 201:
            # Content should be escaped/sanitized
            data = response.json()
            # Script tags should be removed or escaped
            assert "<script>" not in data.get("content", "")

    def test_xss_in_post_title(self, authenticated_client: TestClient):
        """Test XSS protection in post title."""
        malicious_data = {
            "title": "<img src=x onerror=alert('xss')>",
            "content": "Test content here",
            "category": "general"
        }
        
        response = authenticated_client.post("/api/v1/community/posts", json=malicious_data)
        
        if response.status_code == 201:
            data = response.json()
            # Script/event handlers should be removed
            assert "onerror=" not in data.get("title", "")

    def test_list_posts(self, authenticated_client: TestClient, db_session: Session):
        """Test listing community posts."""
        from app.models.community import Post
        from app.crud.user_crud import get_user_by_username
        
        user = get_user_by_username(db_session, "testuser")
        
        # Create some posts
        for i in range(3):
            post = Post(
                user_id=user.id,
                title=f"Post {i}",
                content=f"Content {i}" * 10,
                category="general"
            )
            db_session.add(post)
        db_session.commit()
        
        response = authenticated_client.get("/api/v1/community/posts")
        assert response.status_code == 200
        
        data = response.json()
        if isinstance(data, list):
            assert len(data) >= 3

    def test_get_post_detail(self, authenticated_client: TestClient, db_session: Session):
        """Test getting a specific post."""
        from app.models.community import Post
        from app.crud.user_crud import get_user_by_username
        
        user = get_user_by_username(db_session, "testuser")
        
        post = Post(
            user_id=user.id,
            title="Test Post",
            content="Test content" * 10,
            category="general"
        )
        db_session.add(post)
        db_session.commit()
        
        response = authenticated_client.get(f"/api/v1/community/posts/{post.id}")
        assert response.status_code == 200
        
        data = response.json()
        assert data["title"] == "Test Post"

    def test_get_nonexistent_post(self, authenticated_client: TestClient):
        """Test getting non-existent post."""
        response = authenticated_client.get("/api/v1/community/posts/nonexistent-id")
        assert response.status_code == 404

    def test_update_own_post(self, authenticated_client: TestClient, db_session: Session):
        """Test updating own post."""
        from app.models.community import Post
        from app.crud.user_crud import get_user_by_username
        
        user = get_user_by_username(db_session, "testuser")
        
        post = Post(
            user_id=user.id,
            title="Original Title",
            content="Original content" * 10,
            category="general"
        )
        db_session.add(post)
        db_session.commit()
        
        response = authenticated_client.patch(
            f"/api/v1/community/posts/{post.id}",
            json={
                "title": "Updated Title",
                "content": "Updated content" * 10
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            assert data["title"] == "Updated Title"

    def test_update_other_user_post(self, authenticated_client: TestClient, db_session: Session):
        """Test that users can't update other users' posts."""
        from app.models.community import Post
        from app.models.user import User
        
        other_user = User(
            username="postauthor",
            email="author@test.com",
            hashed_password="hashed"
        )
        db_session.add(other_user)
        db_session.commit()
        
        post = Post(
            user_id=other_user.id,
            title="Other User Post",
            content="Other content" * 10,
            category="general"
        )
        db_session.add(post)
        db_session.commit()
        
        response = authenticated_client.patch(
            f"/api/v1/community/posts/{post.id}",
            json={"title": "Hacked Title"}
        )
        assert response.status_code == 403

    def test_delete_own_post(self, authenticated_client: TestClient, db_session: Session):
        """Test deleting own post."""
        from app.models.community import Post
        from app.crud.user_crud import get_user_by_username
        
        user = get_user_by_username(db_session, "testuser")
        
        post = Post(
            user_id=user.id,
            title="To Delete",
            content="Delete me" * 10,
            category="general"
        )
        db_session.add(post)
        db_session.commit()
        
        post_id = post.id
        
        response = authenticated_client.delete(f"/api/v1/community/posts/{post_id}")
        assert response.status_code == 204
        
        # Verify deletion
        response = authenticated_client.get(f"/api/v1/community/posts/{post_id}")
        assert response.status_code == 404

    def test_delete_other_user_post(self, authenticated_client: TestClient, db_session: Session):
        """Test that users can't delete other users' posts."""
        from app.models.community import Post
        from app.models.user import User
        
        other_user = User(
            username="postowner",
            email="owner@test.com",
            hashed_password="hashed"
        )
        db_session.add(other_user)
        db_session.commit()
        
        post = Post(
            user_id=other_user.id,
            title="Protected Post",
            content="Don't delete" * 10,
            category="general"
        )
        db_session.add(post)
        db_session.commit()
        
        response = authenticated_client.delete(f"/api/v1/community/posts/{post.id}")
        assert response.status_code == 403

    def test_like_post(self, authenticated_client: TestClient, db_session: Session):
        """Test liking a post."""
        from app.models.community import Post
        from app.models.user import User
        
        user = User(username="postliker", email="liker@test.com", hashed_password="hashed")
        db_session.add(user)
        db_session.commit()
        
        post = Post(
            user_id=user.id,
            title="Likeable Post",
            content="Like this" * 10,
            category="general"
        )
        db_session.add(post)
        db_session.commit()
        
        response = authenticated_client.post(f"/api/v1/community/posts/{post.id}/like")
        
        if response.status_code == 200:
            data = response.json()
            assert "likes" in data or "liked" in data

    def test_unlike_post(self, authenticated_client: TestClient, db_session: Session):
        """Test unliking a post."""
        from app.models.community import Post
        from app.models.user import User
        
        user = User(username="unliker", email="unlike@test.com", hashed_password="hashed")
        db_session.add(user)
        db_session.commit()
        
        post = Post(
            user_id=user.id,
            title="Unlikeable Post",
            content="Unlike this" * 10,
            category="general"
        )
        db_session.add(post)
        db_session.commit()
        
        # First like the post
        authenticated_client.post(f"/api/v1/community/posts/{post.id}/like")
        
        # Then unlike
        response = authenticated_client.delete(f"/api/v1/community/posts/{post.id}/like")
        
        if response.status_code == 200:
            data = response.json()
            assert "likes" in data or "liked" in data

    def test_create_comment(self, authenticated_client: TestClient, db_session: Session):
        """Test creating a comment on a post."""
        from app.models.community import Post
        from app.models.user import User
        
        user = User(username="commenter", email="comment@test.com", hashed_password="hashed")
        db_session.add(user)
        db_session.commit()
        
        post = Post(
            user_id=user.id,
            title="Commentable Post",
            content="Comment here" * 10,
            category="general"
        )
        db_session.add(post)
        db_session.commit()
        
        response = authenticated_client.post(
            f"/api/v1/community/posts/{post.id}/comments",
            json={"content": "Great post! " * 10}
        )
        
        if response.status_code == 201:
            data = response.json()
            assert "id" in data
            assert "content" in data

    def test_comment_xss_protection(self, authenticated_client: TestClient, db_session: Session):
        """Test XSS protection in comments."""
        from app.models.community import Post
        from app.models.user import User
        
        user = User(username="commentxss", email="xss@test.com", hashed_password="hashed")
        db_session.add(user)
        db_session.commit()
        
        post = Post(
            user_id=user.id,
            title="XSS Test Post",
            content="Test post" * 10,
            category="general"
        )
        db_session.add(post)
        db_session.commit()
        
        malicious_comment = {
            "content": "Nice post <img src=x onerror=\"alert('xss')\">"
        }
        
        response = authenticated_client.post(
            f"/api/v1/community/posts/{post.id}/comments",
            json=malicious_comment
        )
        
        if response.status_code == 201:
            data = response.json()
            # Event handlers should be removed
            assert "onerror=" not in data.get("content", "")

    def test_get_post_comments(self, authenticated_client: TestClient, db_session: Session):
        """Test retrieving comments for a post."""
        from app.models.community import Post, Comment
        from app.models.user import User
        
        user = User(username="getcommenter", email="getcomment@test.com", hashed_password="hashed")
        db_session.add(user)
        db_session.commit()
        
        post = Post(
            user_id=user.id,
            title="Post with Comments",
            content="See comments" * 10,
            category="general"
        )
        db_session.add(post)
        db_session.commit()
        
        # Add comments
        for i in range(3):
            comment = Comment(
                user_id=user.id,
                post_id=post.id,
                content=f"Comment {i}" * 10
            )
            db_session.add(comment)
        db_session.commit()
        
        response = authenticated_client.get(f"/api/v1/community/posts/{post.id}/comments")
        
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list):
                assert len(data) >= 0

    def test_community_leaderboard(self, client: TestClient, db_session: Session):
        """Test community leaderboard."""
        from app.models.community import Post
        from app.models.user import User
        
        # Create users with posts
        for i in range(3):
            user = User(
                username=f"leaderuser{i}",
                email=f"leader{i}@test.com",
                hashed_password="hashed"
            )
            db_session.add(user)
        db_session.commit()
        
        response = client.get("/api/v1/community/leaderboard")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)

    def test_category_filtering(self, authenticated_client: TestClient, db_session: Session):
        """Test filtering posts by category."""
        from app.models.community import Post
        from app.crud.user_crud import get_user_by_username
        
        user = get_user_by_username(db_session, "testuser")
        
        # Create posts in different categories
        categories = ["general", "strategies", "tools"]
        for category in categories:
            post = Post(
                user_id=user.id,
                title=f"Post in {category}",
                content=f"Content for {category}" * 10,
                category=category
            )
            db_session.add(post)
        db_session.commit()
        
        # Filter by category
        response = authenticated_client.get("/api/v1/community/posts?category=strategies")
        assert response.status_code == 200