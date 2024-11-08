import aiohttp
import asyncio
import json

urls = [
    "https://example.com",
    "https://httpbin.org/status/404",
    "https://nonexistent.url",
]


async def fetch_url(session: aiohttp.ClientSession, url: str) -> dict:
    try:
        async with session.get(url, timeout=5) as response:
            print(url, response.status)
            return {"url": url, "status_code": response.status}
    except (aiohttp.ClientError, asyncio.TimeoutError):
        return {"url": url, "status_code": 0}


async def fetch_urls(urls: list[str], file_path: str):
    connector = aiohttp.TCPConnector(limit=5)
    async with aiohttp.ClientSession(connector=connector) as session:
        tasks = [asyncio.create_task(fetch_url(session, url)) for url in urls]
        results = await asyncio.gather(*tasks)
    with open(file_path, "w") as f:
        for result in results:
            f.write(json.dumps(result) + "\n")


if __name__ == "__main__":
    asyncio.run(fetch_urls(urls, "./results.jsonl"))
