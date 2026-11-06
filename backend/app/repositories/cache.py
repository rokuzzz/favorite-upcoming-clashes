"""Small in-memory TTL cache used by the caching repositories."""

import asyncio
import time
from collections.abc import Awaitable, Callable, Hashable
from typing import Any, TypeVar

T = TypeVar("T")


class TtlCache:
    def __init__(self, clock: Callable[[], float] = time.monotonic) -> None:
        self._clock = clock
        self._entries: dict[Hashable, tuple[float, Any]] = {}
        self._locks: dict[Hashable, asyncio.Lock] = {}

    async def get_or_load(self, key: Hashable, ttl_s: float, loader: Callable[[], Awaitable[T]]) -> T:
        """Return the cached value for key, calling loader() only if it is missing or expired.

        A per-key lock makes concurrent callers share one load instead of all hitting the API.
        """
        if self._is_fresh(key):
            return self._entries[key][1]
        async with self._locks.setdefault(key, asyncio.Lock()):
            if self._is_fresh(key):
                return self._entries[key][1]
            value = await loader()
            self._entries[key] = (self._clock() + ttl_s, value)
            return value

    def _is_fresh(self, key: Hashable) -> bool:
        entry = self._entries.get(key)
        return entry is not None and entry[0] > self._clock()
