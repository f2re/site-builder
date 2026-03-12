import pytest
from httpx import AsyncClient
from unittest.mock import patch

@pytest.mark.anyio
async def test_cms_flow(client: AsyncClient, admin_token: str):
    headers = {"Authorization": f"Bearer {admin_token}"}

    # 1. Create Blog Post via Admin
    post_payload = {
        "title": "Integration Test Post",
        "slug": "integration-test-post",
        "content_json": {"type": "doc", "content": []},
        "meta_title": "SEO Test Title",
        "meta_description": "SEO Test Description",
        "status": "published",
        "tags": ["test", "integration"]
    }
    
    with patch("app.tasks.search.index_blog_post_task.delay") as mock_index:
        resp = await client.post("/api/v1/admin/blog/posts", json=post_payload, headers=headers)
        assert resp.status_code == 201
        assert mock_index.called

    # 2. Get Post (Public)
    public_resp = await client.get("/api/v1/blog/posts/integration-test-post")
    assert public_resp.status_code == 200
    data = public_resp.json()
    assert data["title"] == "Integration Test Post"
    assert data["meta_title"] == "SEO Test Title"

    # 3. Create Page via Admin
    page_payload = {
        "title": "About Us",
        "slug": "about-us",
        "content": "<p>Content</p>",
        "is_active": True
    }
    page_resp = await client.post("/api/v1/admin/pages", json=page_payload, headers=headers)
    assert page_resp.status_code == 201

    # 4. Get Page (Public)
    get_page_resp = await client.get("/api/v1/pages/about-us")
    assert get_page_resp.status_code == 200
    assert get_page_resp.json()["title"] == "About Us"
