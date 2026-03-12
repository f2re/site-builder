# Module: tests/unit/admin/test_migration_html.py | Agent: backend-agent | Task: p11_backend_001
import pytest
import httpx
from unittest.mock import MagicMock
from app.api.v1.admin.migration_service import MigrationService

@pytest.mark.anyio
async def test_html_to_tiptap_nested_tags():
    service = MigrationService(repo=MagicMock(), session=MagicMock())
    html = '<p><span>Text </span><a href="http://example.com"><b>Bold Link</b></a><span> end</span></p>'
    
    result = await service._html_to_tiptap(html)
    
    expected_content = [
        {
            "type": "paragraph",
            "content": [
                {"type": "text", "text": "Text "},
                {
                    "type": "text", 
                    "text": "Bold Link",
                    "marks": [
                        {"type": "link", "attrs": {"href": "http://example.com"}},
                        {"type": "bold"}
                    ]
                },
                {"type": "text", "text": " end"}
            ]
        }
    ]
    assert result["type"] == "doc"
    # Note: order of marks might vary depending on implementation, 
    # but my implementation adds link then bold if it's <a><b>.
    # Actually, in my code:
    # <a> -> new_marks.append(link)
    # <b> -> new_marks.append(bold)
    # So [link, bold] is expected.
    assert result["content"] == expected_content

@pytest.mark.anyio
async def test_html_to_tiptap_strip_unsafe():
    service = MigrationService(repo=MagicMock(), session=MagicMock())
    html = '<p>Safe</p><script>alert(1)</script><iframe></iframe>'
    
    result = await service._html_to_tiptap(html)
    
    assert len(result["content"]) == 1
    assert result["content"][0]["type"] == "paragraph"
    assert result["content"][0]["content"][0]["text"] == "Safe"

@pytest.mark.anyio
async def test_html_to_tiptap_images(monkeypatch):
    service = MigrationService(repo=MagicMock(), session=MagicMock())
    
    # Mock _download_image
    async def mock_download(client, url, folder):
        return f"local://{url.split('/')[-1]}"
    
    monkeypatch.setattr(service, "_download_image", mock_download)
    
    html = '<p>Text</p><img src="http://example.com/img.jpg" alt="alt text">'
    client = httpx.AsyncClient()
    
    result = await service._html_to_tiptap(html, client=client)
    
    assert len(result["content"]) == 2
    assert result["content"][1]["type"] == "image"
    assert result["content"][1]["attrs"]["src"] == "local://img.jpg"
    assert result["content"][1]["attrs"]["alt"] == "alt text"

@pytest.mark.anyio
async def test_html_to_tiptap_problematic_html():
    service = MigrationService(repo=MagicMock(), session=MagicMock())
    html = """
    <p><span>Программный модуль (прошивка для адаптера </span><a href="http://mad-auto.ru/index.php?route=product/product&amp;path=64_65&amp;product_id=51" target="_blank">WiFi OBD2</a><span>) WiFi Dashboard...</span></p>
    <iframe id="docIframe" src="..." ...></iframe>
    <script>...</script>
    <img style="width: 100%;" src="http://example.com/sport-Round3.jpg" alt="sport-Round3" border="0">
    """
    
    async def mock_download(client, url, folder):
        return f"local://{url.split('/')[-1]}"
    service._download_image = mock_download
    
    result = await service._html_to_tiptap(html, client=httpx.AsyncClient())
    
    # 1. Paragraph
    # 2. Image (since script and iframe are stripped)
    assert len(result["content"]) == 2
    assert result["content"][0]["type"] == "paragraph"
    assert result["content"][1]["type"] == "image"
    
    # Check link in paragraph
    para_content = result["content"][0]["content"]
    link_node = next(n for n in para_content if n.get("marks") and any(m["type"] == "link" for m in n["marks"]))
    assert link_node["text"] == "WiFi OBD2"
    assert any(m["attrs"]["href"].startswith("http://mad-auto.ru") for m in link_node["marks"])
