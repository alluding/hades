from typing import Any, Dict, List, Optional

import asyncio
import datetime

class InvalidOperation(Exception):
    pass

class ExpiringDict:
    def __init__(self) -> None:
        self.dict: Dict[str, Any] = {}
        self.rl: Dict[str, int] = {}

        self.delete: Dict[str, Dict[str, int]] = {}
        self.futures: Dict[str, asyncio.Future] = {}

    async def do_expiration(self, key: str, expiration: int) -> None:
        await asyncio.sleep(expiration)

        if key in self.dict:
            self.dict.pop(key)
            self.delete.pop(key, None)
            self.futures.pop(key, None)

    async def do_cancel(self, key: str) -> None:
        if key in self.futures:
            self.futures[key].cancel()
            self.futures.pop(key)

    async def set(self, key: str, value: Any, expiration: int = 60) -> int:
        await self.do_cancel(key)
        self.dict[key] = value

        if expiration > 0:
            self.futures[key] = asyncio.ensure_future(
                self.do_expiration(key, expiration))

        return 1

    async def remove(self, key: str) -> int:
        await self.do_cancel(key)
        return 1 if self.dict.pop(key, None) is not None else 0

    async def get(self, key: str) -> Any:
        return self.dict.get(key, None)

    async def sadd(self, key: str, *values: Any, position: int = 0, expiration: int = 0) -> int:
        await self.do_cancel(key)

        if key not in self.dict:
            self.dict[key] = []

        if not isinstance(self.dict[key], list):
            raise InvalidOperation(f"Key '{key}' exists but is not a list.")

        self.dict[key][position:position] = list(values)

        if expiration > 0:
            self.futures[key] = asyncio.ensure_future(
                self.do_expiration(key, expiration)
            )

        return 1

    async def sismember(self, key: str, value: Any) -> bool:
        return key in self.dict and value in self.dict[key]

    async def smembers(self, key: str) -> Optional[set]:
        return set(self.dict[key]) if key in self.dict and isinstance(self.dict[key], list) else None

    async def srem(self, key: str, value: Any) -> int:
        if key in self.dict and isinstance(self.dict[key], list) and value in self.dict[key]:
            self.dict[key].remove(value)
            return 1

        return 0

    async def keys(self) -> List[str]:
        return list(self.dict.keys())

    async def do_delete(self, key: str) -> None:
        self.dict.pop(key, None)
        self.delete[key] = {"last": int(datetime.datetime.now().timestamp())}

    def is_ratelimited(self, key: str) -> bool:
        return key in self.dict and self.dict[key] >= self.rl.get(key, 0)

    def time_remaining(self, key: str) -> int:
        last = self.delete.get(key, {}).get("last", 0)
        remaining = (
            last + self.delete.get(key, {}).get("bucket", 60)
        ) - int(datetime.datetime.now().timestamp())

        return max(remaining, 0) if key in self.dict and self.dict[key] >= self.rl.get(key, 0) else 0

    async def ratelimit(self, key: str, amount: int, bucket: int = 60) -> bool:
        self.dict.setdefault(key, 0)
        self.rl.setdefault(key, amount)
        self.delete.setdefault(key, {"bucket": bucket, "last": 0})

        if self.delete[key]["last"] + bucket <= int(datetime.datetime.now().timestamp()):
            await self.do_delete(key)
            self.dict[key] = 0

        self.dict[key] += 1
        return self.dict[key] >= self.rl[key]
