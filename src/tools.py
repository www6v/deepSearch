
from util import segment_rc
from util import rerank

import os
import aiohttp
from typing import (
    List,
    TypedDict,
)


class ScrapTool:
    def __init__(self, gather_links: bool = True) -> None:
        self.gather_links = gather_links

    async def __call__(self, input: str, context: str | None) -> str:
        result = await self.scrap_webpage(input, context)
        return result

    async def scrap_webpage(self, url: str, context: str | None) -> str:
        url = f"https://r.jina.ai/{url}"

        headers = {"X-Retain-Images": "none", "X-With-Links-Summary": "true"}

        if api_key := os.getenv("JINA_API_KEY"):
            headers["Authorization"] = f"Bearer {api_key}"

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers) as response:
                    if response.status != 200:
                        print(f"Failed to fetch {url}: {response.status}")
                        raise Exception(f"Failed to fetch {url}: {response.status}")
                    result = await response.text()

            if context is not None:
                split_fn = lambda t: segment_rc(t)
                merge_fn = lambda t: "\n".join(t)

                reranked = await rerank(
                    result, context, split_fn=split_fn, merge_fn=merge_fn
                )

                result = reranked

            return result

        except Exception as e:
            raise e



class SearchResult(TypedDict):
    url: str
    title: str
    description: str


class SearchTool:
    def __init__(self, timeout: int = 60 * 5) -> None:
        self.timeout = timeout

    async def __call__(self, input: str, *args) -> str:
        results = await self.search(input)
        formatted_results = self._format_results(results)
        return formatted_results

    async def search(self, query: str) -> List[SearchResult]:
        url = f"https://s.jina.ai/{quote_plus(query)}"

        headers = {
            "Accept": "application/json",
            "X-Retain-Images": "none",
            "X-No-Cache": "true",
        }

        if api_key := os.getenv("JINA_API_KEY"):
            headers["Authorization"] = f"Bearer {api_key}"

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    url, headers=headers, timeout=self.timeout
                ) as response:
                    if response.status != 200:
                        print(f"Failed to fetch {url}: {response.status}")
                        raise Exception(f"Failed to fetch {url}: {response.status}")

                    json_response = await response.json()

            results = [
                SearchResult(
                    url=result["url"],
                    title=result["title"],
                    description=result["description"],
                )
                for result in json_response["data"]
            ]

            return results

        except Exception as e:
            raise e

    def _format_results(self, results: List[SearchResult]) -> str:
        formatted_results = []

        for i, result in enumerate(results, 1):
            formatted_results.extend(
                [
                    f"Title: {result['title']}",
                    f"URL Source: {result['url']}",
                    f"Description: {result['description']}",
                    "",
                ]
            )

        return "\n".join(formatted_results).rstrip()
