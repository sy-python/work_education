import aiohttp
import asyncio
import json

urls = [
    "https://example.com",
    "https://httpbin.org/status/404",
    "https://nonexistent.url",
]

file_lock = asyncio.Lock()
url_queue = asyncio.Queue()


async def worker(session: aiohttp.ClientSession, file_path: str) -> dict:
    url = await url_queue.get()
    try:
        async with session.get(url, timeout=5) as response:
            result = {"url": url, "status_code": response.status}
    except aiohttp.ClientResponseError as e:
        result = {"url": url, "status_code": e.status}
    except (aiohttp.ClientError, asyncio.TimeoutError):
        result = {"url": url, "status_code": 0}
    async with file_lock:
        with open(file_path, "a") as f:
            f.write(json.dumps(result) + "\n")
    url_queue.task_done()


async def fetch_urls(urls: list[str], file_path: str):
    async with aiohttp.ClientSession() as session:
        tasks = [asyncio.create_task(worker(session, file_path)) for _ in range(5)]
        for url in urls:
            await url_queue.put(url)
        await url_queue.join()
        for task in tasks:
            task.cancel()


if __name__ == "__main__":
    with open("./results.jsonl", "w") as f:
        pass
    asyncio.run(fetch_urls(urls, "./results.jsonl"))
