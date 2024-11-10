import json
from typing import Any, Callable, Awaitable

import aiohttp
import uvicorn

type Scope = dict[str, Any]
type Receive = Callable[[], Awaitable[Scope]]
type Send = Callable[[Scope], Awaitable[None]]


async def app(scope: Scope, receive: Receive, send: Send) -> None:
    if scope["type"] != "http":
        raise ValueError("Only HTTP is supported")

    currency = scope["path"].removeprefix("/")

    async with aiohttp.ClientSession() as session:
        async with session.get(
            f"https://api.exchangerate-api.com/v4/latest/{currency}"
        ) as response:
            data = await response.json()

    await send(
        {
            "type": "http.response.start",
            "status": response.status,
        }
    )

    await send(
        {
            "type": "http.response.body",
            "body": json.dumps(data).encode(),
        },
    )


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
