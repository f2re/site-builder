# Module: integrations/meilisearch.py | Agent: backend-agent | Task: BE-01
from meilisearch_python_sdk import AsyncClient
from app.core.config import settings
from typing import Any, Dict, List, Optional


class MeilisearchProvider:
    def __init__(self, host: str, api_key: str):
        self.client = AsyncClient(host, api_key)

    async def search(
        self,
        index_name: str,
        query: str,
        limit: int = 20,
        offset: int = 0,
        filter: Optional[List[str]] = None,
        sort: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Proxy search call to Meilisearch.
        """
        index = self.client.index(index_name)
        result = await index.search(
            query,
            limit=limit,
            offset=offset,
            filter=filter,
            sort=sort,
        )
        # SearchResults is a pydantic model in meilisearch-python-sdk
        return result.model_dump()


meilisearch_provider = MeilisearchProvider(
    host=settings.MEILISEARCH_HOST,
    api_key=settings.MEILISEARCH_API_KEY,
)
