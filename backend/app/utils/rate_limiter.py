import threading
import time
from collections import defaultdict, deque


class InMemoryRateLimiter:

    def __init__(self, max_requests: int, window_seconds: int):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._storage = defaultdict(deque)
        self._lock = threading.Lock()

    def reset(self):
        with self._lock:
            self._storage.clear()

    def check(self, key: str):
        current_time = time.time()

        with self._lock:
            queue = self._storage[key]
            cutoff = current_time - self.window_seconds

            while queue and queue[0] <= cutoff:
                queue.popleft()

            if len(queue) >= self.max_requests:
                retry_after = int(max(1, self.window_seconds - (current_time - queue[0])))
                return False, 0, retry_after

            queue.append(current_time)
            remaining = max(0, self.max_requests - len(queue))
            return True, remaining, 0
