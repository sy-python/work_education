import aiohttp
import asyncio
import json

urls = [
    "https://example.com",
    "https://httpbin.org/status/404",
    "https://nonexistent.url",
]

url_queue = asyncio.Queue()
write_queue = asyncio.Queue()


async def request(session: aiohttp.ClientSession, url: str) -> dict:
    try:
        async with session.get(url, timeout=5) as response:
            return {"url": url, "status_code": response.status}
    except aiohttp.ClientResponseError as e:
        return {"url": url, "status_code": e.status}
    except (aiohttp.ClientError, asyncio.TimeoutError):
        return {"url": url, "status_code": 0}


async def worker(session: aiohttp.ClientSession):
    url = await url_queue.get()
    result = await request(session, url)
    write_queue.put(result)
    url_queue.task_done()


async def writer(file_path: str):
    while True:
        result = await write_queue.get()
        with open(file_path, "a") as f:
            f.write(json.dumps(result) + "\n")
        write_queue.task_done()


async def fetch_urls(urls: list[str], file_path: str):
    async with aiohttp.ClientSession() as session:
        tasks = [asyncio.create_task(worker(session)) for _ in range(5)]
        write = asyncio.create_task(writer(file_path))
        for url in urls:
            await url_queue.put(url)
        await url_queue.join()
        for task in tasks:
            task.cancel()
        await write_queue.join()
        write.cancel()


if __name__ == "__main__":
    with open("./results.jsonl", "w") as f:
        pass
    asyncio.run(fetch_urls(urls, "./results.jsonl"))
