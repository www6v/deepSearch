import os
import json
from typing import (
    Any,    
    Callable,
    Iterator,
    List,
)

import aiohttp
from langchain_text_splitters import RecursiveCharacterTextSplitter


def extract_json_values(text: str) -> Iterator[Any]:
    decoder = json.JSONDecoder()

    def next_json_position(pos: int) -> int | None:
        matches = [p for p in (text.find(c, pos) for c in "{[") if p != -1]
        return min(matches) if matches else None

    pos = 0
    while (next_pos := next_json_position(pos)) is not None:
        try:
            result, index = decoder.raw_decode(text[next_pos:])
            yield result
            pos = next_pos + index
        except json.JSONDecodeError:
            pos = next_pos + 1


def extract_largest_json(text: str) -> dict:
    try:
        json_values = list(extract_json_values(text))
        if not json_values:
            raise ValueError("No JSON found in response")
        return max(json_values, key=lambda x: len(json.dumps(x)))
    except Exception as e:
        raise ValueError(f"Failed to extract JSON: {str(e)}\nText: {text}")


def segment_rc(text: str, chunk_size=1000, chunk_overlap=500) -> List[str]:
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
        is_separator_regex=False,
    )

    texts = text_splitter.split_text(text)
    return texts



async def rerank(
    text: str,
    query: str,
    top_docs: int = 5,
    split_fn: Callable[[str], list[str]] | None = None,
    merge_fn: Callable[[List[str]], str] | None = None,
) -> str:
    url = f"https://api.jina.ai/v1/rerank"

    headers = {
        "Content-Type": "application/json",
    }

    if api_key := os.getenv("JINA_API_KEY"):
        headers["Authorization"] = f"Bearer {api_key}"

    if not split_fn:
        split_fn = segment_rc

    if not merge_fn:
        merge_fn = lambda t: "\n".join(t)

    chunks = split_fn(text)

    data = {
        "model": "jina-reranker-v2-base-multilingual",
        "query": query,
        "top_n": top_docs,
        "documents": chunks,
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=data) as response:
                if response.status != 200:
                    print(f"Failed to fetch {url}: {response.status}")
                    raise Exception(f"Failed to fetch {url}: {response.status}")

                data = await response.json()
                results = [result["document"]["text"] for result in data["results"]]
                merged_text = merge_fn(results)
                return merged_text

    except Exception as e:
        raise e